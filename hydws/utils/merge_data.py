
"""
Provide facilities for importing json data.
"""
import logging
import io
import json
from sqlalchemy.orm import subqueryload

# TODO (sarsonl) make version loading dynamic
from hydws.db.orm import Borehole, BoreholeSection, HydraulicSample
from hydws.server.v1.ostream.schema import BoreholeSchema


logger = logging.getLogger(__name__)


def load_json(input_data, context, schema_class=BoreholeSchema):
    """
    Loads a json file or string of data
    and deserializes it based on BoreholeSchema.

    :param opened_file: file object containing JSON data
    :param schema: Schema class to deserialize data
    :param schema_args: dict of args to pass to schema instance


    :rtype: List or single instance of orm.Borehole
    """
    if isinstance(input_data, io.IOBase):
        data = json.load(input_data)
    elif isinstance(input_data, str):
        data = json.loads(input_data)
    elif isinstance(input_data, dict):
        data = input_data
    else:
        raise IOError(f"input data of type: {type(input_data)}"
                      " and cannot be read.")

    many = False
    if isinstance(data, list):
        many = True

    schema = schema_class(many=many)
    schema.context = context
    loaded_data = schema.load(data)
    return loaded_data, many


def replace_hydraulics(section, section_existing, session):
    # Get time range of imported dataset
    first_sample = min(h.datetime_value for h in section._hydraulics)
    last_sample = max(h.datetime_value for h in section._hydraulics)
    row_count = session.query(HydraulicSample).filter(
        HydraulicSample.datetime_value>=first_sample).\
        filter(HydraulicSample.datetime_value <= last_sample).\
        filter(HydraulicSample.boreholesection_oid== # noqa
               section_existing._oid).delete()
    logger.info(f"{row_count} hydraulic samples deleted. ")
    session.commit()
    section_existing = session.query(BoreholeSection).\
        options(subqueryload("_hydraulics")).\
        filter(
            BoreholeSection.publicid == section.publicid).one_or_none()

    copied_samples = [sample.copy() for sample in section._hydraulics]
    section_existing._hydraulics.extend(copied_samples)
    logger.info("Samples added to hydraulic well section "
                f"{section_existing.publicid}: "
                f"{len(copied_samples)}. ")
    logger.info("Total samples in hydraulic well section "
                f"{section_existing.publicid}: "
                f"{len(section_existing._hydraulics)}. ")
    info = (f" {row_count} hydraulic samples deleted. "
            "Samples added to hydraulic well section "
            f"{section_existing.publicid}: "
            f"{len(copied_samples)}. "
            "Total samples in hydraulic well section "
            f"{section_existing.publicid}: "
            f"{len(section_existing._hydraulics)}.")
    session.add_all(copied_samples)
    session.commit()
    return info

def set_well_data(well, well_existing, session):
    well_existing.longitude_value = well.longitude_value
    well_existing.latitude_value = well.latitude_value
    well_existing.altitude_value = well.altitude_value
    well_existing.depth_value = well.depth_value
    well_existing.bedrockdepth_value = well.bedrockdepth_value
    well_existing.measureddepth_value = well.measureddepth_value
    session.commit()

def set_section_data(section, section_existing, session):
    section_existing.endtime = section.endtime
    section_existing.starttime = section.starttime
    section_existing.toplatitude_value = section.toplatitude_value
    section_existing.toplongitude_value = section.toplongitude_value
    section_existing.bottomlatitude_value = section.bottomlatitude_value
    section_existing.bottomlongitude_value = section.bottomlongitude_value
    section_existing.topdepth_value = section.topdepth_value
    section_existing.bottomdepth_value = section.bottomdepth_value
    section_existing.holediameter_value = section.holediameter_value
    section_existing.casingdiameter_value = section.casingdiameter_value
    session.commit()

def merge_boreholes(data, session,
                    assignids=None,
                    publicid_uri=None,
                    overwrite_publicids=None,
                    merge_only=None):
    """Function to be called from load_data script or
    by POST request to either add or merge a Borehole
    to the database, replacing any overlapping data.
    """
    context = {}
    if assignids:
        context = {
            'publicid_uri': publicid_uri,
            'overwrite': overwrite_publicids}

    deserialized_data, many_boreholes = load_json(
        data, context)

    logger.debug('Adding data to db...')
    bhs_info = ""

    if not many_boreholes:
        deserialized_data = [deserialized_data]
    for bh in deserialized_data:
        bh_existing = session.query(Borehole).\
            options(subqueryload("_sections").
                    subqueryload("_hydraulics")).\
            filter(
            Borehole.publicid == bh.publicid).one_or_none()
        bh_info = (f"Borehole {bh.publicid} "
                   f"already in db: {False if bh_existing is None else True}.")
        if bh_existing:
            set_well_data(bh, bh_existing, session)
            logger.info("A borehole exists with the same "
                        "publicid. Merging with existing "
                        "borehole.")
            for section in bh._sections:
                section_existing = session.query(BoreholeSection).\
                    options(subqueryload("_hydraulics")).\
                    filter(BoreholeSection.publicid== # noqa
                           section.publicid).one_or_none()
                if section_existing:
                    hyd_info = replace_hydraulics(section,
                                                  section_existing,
                                                  session)
                    set_section_data(section,
                                     section_existing,
                                     session)

                else:
                    hyd_info = (f"section {section.publicid} "
                                "being fully copied.")
                    section_copy = section.copy()
                    section_copy._borehole = bh_existing
                bh_info += hyd_info
        else:
            if merge_only:
                raise ValueError(
                    "No borehole exists with publicid: "
                    f"{bh.publicid} and cannot be merged.")
            session.add(bh)
            bh_info += "Borehole has been created in db."
        bhs_info += bh_info

    try:
        session.commit()
        logger.info(
            "Data successfully imported to db.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        return (bhs_info + " Data successfully added to db. ")
