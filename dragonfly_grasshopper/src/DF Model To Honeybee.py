# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a Dragonfly Model into a series of Honeybee Models.
-

    Args:
        _model: A Dragonfly Model object.
        _obj_per_model_: Text to describe how the input Buildings should be divided
            across the output Models. Default: 'Building'. Choose from the
            following options:
                * District - All buildings will be added to a single Honeybee Model.
                    Such a Model can take a long time to simulate so this is only
                    recommended for small numbers of buildings.
                * Building - Each input building will be exported into its own Model.
                    For each Model, the other buildings input to this component will
                    appear as context shade geometry. Thus, each Model is its own
                    simulate-able unit.
        use_multiplier_: If True, the multipliers on each Building's Stories will be
            passed along to the generated Honeybee Room objects, indicating the
            simulation will be run once for each unique room and then results
            will be multiplied. If False, full geometry objects will be written
            for each and every story in the building such that all resulting
            multipliers will be 1. (Default: True).
        add_plenum_: Boolean to indicate whether ceiling/floor plenums should
            be auto-generated for the Rooms. The height of ceiling plenums
            will be autocalculated as the difference between the Room2D
            ceiling height and Story ceiling height. The height of the floor
            plenum will be autocalculated as the difference between the Room2D
            floor height and Story floor height. (Default: False).
        shade_dist_: An optional number to note the distance beyond which other
            buildings' shade should not be exported into a given Model. This is
            helpful for reducing the simulation run time of each Model when other
            connected buildings are too far away to have a meaningful impact on
            the results. If None, all other buildings will be included as context
            shade in each and every Model. Set to 0 to exclude all neighboring
            buildings from the resulting models. Default: None.
        _run: Set to "True" to have the Dragonfly Model translated to a series
            of Honeybee Models.
    
    Returns:
        report: Reports, errors, warnings, etc.
        hb_models: Honeybee Model objects derived from the input _models. These
            Models are ready to be simulated in either an Energy or Radiance
            simulation or they can be edited further with the Honeybee
            components.
"""

ghenv.Component.Name = 'DF Model To Honeybee'
ghenv.Component.NickName = 'ToHoneybee'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'


try:  # import the core dragonfly dependencies
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set default inputs if not specified
    use_multiplier_ = use_multiplier_ if use_multiplier_ is not None else True
    add_plenum_ = add_plenum_ if add_plenum_ is not None else False
    _obj_per_model_ = 'Building' if _obj_per_model_ is None else _obj_per_model_

    # check the _model input
    assert isinstance(_model, Model), \
        'Expected Dragonfly Model object. Got {}.'.format(type(_model))

    # create the model objects
    hb_models = _model.to_honeybee(
        _obj_per_model_, shade_dist_, use_multiplier_, add_plenum_,
        tolerance=tolerance)
