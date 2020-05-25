# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a Dragonfly Model into an URBANopt-compatible geoJSON with linked Honeybee
Model JSONs. Honeybee Model JSONs will be referenced using the "detailed_model_filename"
key in the geoJSON.
-

    Args:
        _model: A Dragonfly Model object.
        _location: A ladybug Location object possessing longitude and lattiude data
            used to position geoJSON file on the globe.
        _point_: A Point for where the _location object exists within the space of
            the Rhino scene. This is used to posistion the geoJSON file on the
            globe. (Default: Rhino origin (0, 0, 0)).
        use_multiplier_: If True, the multipliers on each Building's Stories will be
            passed along to the generated Honeybee Room objects, indicating the
            simulation will be run once for each unique room and then results
            will be multiplied. If False, full geometry objects will be written
            for each and every story in the building such that all resulting
            multipliers will be 1. Default: True.
        shade_dist_: An optional number to note the distance beyond which other
            buildings' shade should not be exported into a given Model. This is
            helpful for reducing the simulation run time of each Model when other
            connected buildings are too far away to have a meaningful impact on
            the results. If None, all other buildings will be included as context
            shade in each and every Model. Set to 0 to exclude all neighboring
            buildings from the resulting models. Default: None.
        _folder_: Text for the full path to the folder where the geojson will be
            written along with all of the Honeybee Model JSONs. If None, the
            honeybee default simulation folder is used.
        _write: Set to "True" to have the Dragonfly Model translated to an
            URBANopt-compatible geoJSON.
    
    Returns:
        report: Reports, errors, warnings, etc.
        geojson: The path to a geoJSON file that contains polygons for all of the
            Buildings within the dragonfly model along with their properties
            (floor area, number of stories, etc.). The polygons will also possess
            detailed_model_filename keys that align with where the Honeybee Model
            JSONs are written.
        hb_jsons: A list of file paths to honeybee Model JSONS that correspond to
            the detailed_model_filename keys in the geojson.
        hb_models: A list of honeybee Model objects that were generated in process
            of writing the URBANopt files. These can be visulazed using the
            components in the Honeybee 1 :: Visualize tab in order to verify
            that properties have been translated as expected.
"""

ghenv.Component.Name = 'DF Model To geoJSON'
ghenv.Component.NickName = 'ToGeoJSON'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'


try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d.pointvector import Point2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the ladybug dependencies
    from ladybug.location import Location
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point2d
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _write:
    # set default inputs if not specified
    point = to_point2d(_point_) if _point_ is not None else Point2D(0, 0)
    use_multiplier_ = use_multiplier_ if use_multiplier_ is not None else True

    # check the _model and _location input
    assert isinstance(_model, Model), \
        'Expected Dragonfly Model object. Got {}.'.format(type(_model))
    assert isinstance(_location, Location), \
        'Expected Ladybug Location object. Got {}.'.format(type(_location))

    # create the geoJSON and honeybee Model JSONs
    geojson, hb_jsons, hb_models = _model.to.urbanopt(
        _model, _location, point, shade_dist_, use_multiplier_, _folder_,
        tolerance)
