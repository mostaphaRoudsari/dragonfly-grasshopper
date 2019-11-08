# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Dragonfly Building from individual Dragonfly Story objects.
-

    Args:
        _stories: A list of Dragonfly Story objects to be joined into one Building.
        multipliers_: An optional list of integers with the same length as the
            input _stories, which will be used to override any existing multipliers
            on the input Story objects. This integer denotes the number of times
            that each Story is repeated over the height of the building. If
            nothing is input here, the multipliers on the existing Story objects
            will remain.
        _name_:  A name for the Building. If the name is not provided a random
            name will be assigned
        _constr_set_: Text for the construction set of the Building, which is used
            to assign all default energy constructions needed to create an energy
            model. Text should refer to a ConstructionSet within the library such
            as that output from the "HB List Construction Sets" component. This
            can also be a custom ConstructionSet object. If nothing is input here,
            the Building will have a generic construction set that is not sensitive
            to the Buildings's climate or building energy code.
    
    Returns:
        report: Reports, errors, warnings, etc.
        building: Dragonfly Building.
"""

ghenv.Component.Name = "DF Building from Stories"
ghenv.Component.NickName = 'BuildingStories'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

# document-wide counter to generate new unique Building names
import scriptcontext
try:
    scriptcontext.sticky["bldg_count"]
except KeyError:  # first time that the component is running
    scriptcontext.sticky["bldg_count"] = 1

try:  # import the core dragonfly dependencies
    from dragonfly.building import Building
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
    from honeybee_energy.lib.constructionsets import construction_set_by_name
except ImportError as e:
    if _constr_set_ is not None:
        raise ValueError('_constr_set_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    stories = [story.duplicate() for story in _stories]
    
    # if there are multipliers, use them to reassign the story multipliers
    if len(multipliers_) != 0:
        assert len(multipliers_) == len(stories), 'Length of input multipliers_ ' \
            '({}) does not match the length of input _stories ({}).'.format(
                len(multipliers_), len(_stories))
        for mult, story in zip(multipliers_, stories):
            story.multiplier = mult
    
    # generate a default name
    if _name_ is None:  # get a default Building name
        _name_ = "Building_{}".format(scriptcontext.sticky["bldg_count"])
        scriptcontext.sticky["bldg_count"] += 1
    
    # create the Building
    building = Building(_name_, stories)
    
    # assign the construction set
    if _constr_set_ is not None:
        if isinstance(_constr_set_, str):
            _constr_set_ = construction_set_by_name(_constr_set_)
        building.properties.energy.construction_set = _constr_set_