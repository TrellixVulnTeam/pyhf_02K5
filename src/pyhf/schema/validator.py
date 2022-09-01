import jsonschema
import logging
import pyhf.exceptions
from pyhf.schema.loader import load_schema
from pyhf.schema import variables
from typing import Union, Mapping

log = logging.getLogger(__name__)


def validate(spec: Mapping, schema_name: str, version: Union[str, None] = None):
    """
    Validate a provided specification against a schema.

    Args:
        spec (dict): The specification to validate.
        schema_name (str): The name of the schema to use.
        version (None or str): The version to use if not the default from :attr:`pyhf.schema.version`.

    Returns:
        None: schema validated fine

    Raises:
        pyhf.exceptions.InvalidSpecification: the specification is invalid
    """

    version = version or variables.SCHEMA_VERSION
    if version != variables.SCHEMA_VERSION:
        log.warning(
            f"Specification requested version {version} but latest is {variables.SCHEMA_VERSION}. Upgrade your specification or downgrade pyhf."
        )

    schema = load_schema(f'{version}/{schema_name}')

    # note: trailing slash needed for RefResolver to resolve correctly
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{variables.schemas}/{version}/{schema_name}",
        referrer=load_schema(f"{version}/defs.json"),
        store=variables.SCHEMA_CACHE,
    )
    validator = jsonschema.Draft202012Validator(
        schema, resolver=resolver, format_checker=None
    )

    try:
        return validator.validate(spec)
    except jsonschema.ValidationError as err:
        raise pyhf.exceptions.InvalidSpecification(err, schema_name)
