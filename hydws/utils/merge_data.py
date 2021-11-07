
"""
Provide facilities for importing json data.
"""
import logging
import io
import json
from sqlalchemy.orm import subqueryload
from sqlalchemy import inspect

# TODO (sarsonl) make version loading dynamic
from hydws.db.orm import Borehole, BoreholeSection, HydraulicSample
from hydws.server.v1.ostream.schema import (
    BoreholeSchema)

EXCLUDE_ATTRS = ["sections", "hydraulics", "_oid", "public_id", "borehole_oid"]

logger = logging.getLogger(__name__)


def load_json(input_data, context, schema_class=BoreholeSchema,
              merge_only=False):
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
    try:
        # loat partial data only if merge_only is selected
        loaded_data = schema.load(data, partial=merge_only)
    except Exception as err:
        raise IOError(
            f"input data cannot be read into schema {err}")
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

def replace_attr(existing_obj, new_obj, attr):
    info = ''
    existing_attr_value = getattr(existing_obj, attr)
    new_attr_value = getattr(new_obj, attr)
    if new_attr_value is not None:
        if existing_attr_value != new_attr_value:
            setattr(existing_obj, attr, new_attr_value)
            info = (f"Replacing attr {attr} from {existing_attr_value} "
                    f"to {new_attr_value}. ")
    else:
        if existing_attr_value is not None:
            info = (f"Keeping attr {attr} as {existing_attr_value}. "
                    "rather than setting to None. ")
            logger.info(info)
    return info

def replace_metadata(existing_obj, new_obj, session, orm_class):
    attr_info = ''
    inst = inspect(orm_class)
    attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
    attr_list = [attr for attr in attr_names if attr not in EXCLUDE_ATTRS]
    for attr in attr_list:
        attr_info += replace_attr(existing_obj, new_obj, attr)

    session.commit()
    return attr_info

def merge_boreholes(data, session,
                    assignids=None,
                    publicid_uri=None,
                    overwrite_publicids=None,
                    merge_only=False):
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
        data, context, merge_only=merge_only)

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
            bh_attr_info = replace_metadata(bh_existing, bh, session,
                                            Borehole)
            bhs_info += bh_attr_info
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
                    sec_attr_info = replace_metadata(section_existing,
                                                     section, session,
                                                     BoreholeSection)
                    bhs_info += sec_attr_info
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
