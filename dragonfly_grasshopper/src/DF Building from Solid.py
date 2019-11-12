# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Dragonfly Buildings from solid geometry (closed Rhino polysurfaces).
-

    Args:
        _bldg_geo: A list of closed Rhino polysurfaces to be converted into Buildings.
        _floor_to_floor: An array of floor-to-floor height instructions
            that describe how a building mass should be divided into floors.
            The array should run from bottom floor to top floor.
            Each item in the array can be either a single number for the
            floor-to-floor height or a text string that codes for how many
            floors of each height should be generated.  For example, inputting
            "2@4" will make two floors with a height of 4 units. Simply inputting
            "@3" will make all floors at 3 units.  Putting in sequential arrays
            of these text strings will divide up floors accordingly.  For example,
            the list ["1@5", "2@4", "@3"]  will make a ground floor of 5 units,
            two floors above that at 4 units and all remaining floors at 3 units.
        _name_: A base name to be used for the Buildings. This will be combined
            with the index of each input _geo to yield a unique name for each
            output Building.
        _program_: Text for the program of the Buildings (to be looked up in the
            ProgramType library) such as that output from the "HB List Programs"
            component. This can also be a custom ProgramType object. If no program
            is input here, the Buildings will have a generic office program.
        _constr_set_: Text for the construction set of the Buildings, which is used
            to assign all default energy constructions needed to create an energy
            model. Text should refer to a ConstructionSet within the library such
            as that output from the "HB List Construction Sets" component. This
            can also be a custom ConstructionSet object. If nothing is input here,
            the Buildings will have a generic construction set that is not sensitive
            to the Buildings's climate or building energy code.
        conditioned_: Boolean to note whether the Buildings have heating and cooling
            systems.
        _run: Set to True to run the component and create Dragonfly Buildings.
    
    Returns:
        report: Reports, errors, warnings, etc.
        buildings: Dragonfly buildings.
"""

ghenv.Component.Name = "DF Building from Solid"
ghenv.Component.NickName = 'BuildingSolid'
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
    from dragonfly.subdivide import interpret_floor_height_subdivide
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.intersect import split_solid_to_floors, geo_min_max_height
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the dragonfly-energy extension
    import dragonfly_energy
    from honeybee_energy.lib.programtypes import program_type_by_name, office_program
    from honeybee_energy.lib.constructionsets import construction_set_by_name
    from honeybee_energy.idealair import IdealAirSystem
except ImportError as e:
    if _program_ is not None:
        raise ValueError('_program_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))
    elif _constr_set_ is not None:
        raise ValueError('_constr_set_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))
    elif conditioned_ is not None:
        raise ValueError('conditioned_ has been specified but dragonfly-energy '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    buildings = []  # list of buildings that will be returned
    
    for i, geo in enumerate(_bldg_geo):
        # get the name for the Building
        if _name_ is None:  # make a default Building name
            name = "Building_{}".format(scriptcontext.sticky["bldg_count"])
            scriptcontext.sticky["bldg_count"] += 1
        else:
            name = '{}_{}'.format(_name_, i + 1)
        
        # interpret the input _floor_to_floor information
        min, max = geo_min_max_height(geo)
        floor_heights, interpreted_f2f = interpret_floor_height_subdivide(
            _floor_to_floor, max, min)
        
        # get the floor geometries of the building
        floor_breps = split_solid_to_floors(geo, floor_heights)
        floor_faces = [to_face3d(flr) for flr in floor_breps]
        
        # create the Building
        building = Building.from_all_story_geometry(name, floor_faces,
                                                    interpreted_f2f, tolerance)
        
        # assign the program
        if _program_ is not None:
            if isinstance(_program_, str):
                _program_ = program_type_by_name(_program_)
            building.properties.energy.set_all_room_2d_program_type(_program_)
        else:  # generic office program by default
            try:
                building.properties.energy.set_all_room_2d_program_type(office_program)
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed
        
        # assign the construction set
        if _constr_set_ is not None:
            if isinstance(_constr_set_, str):
                _constr_set_ = construction_set_by_name(_constr_set_)
            building.properties.energy.construction_set = _constr_set_
        
        # assign an ideal air system
        if conditioned_ or conditioned_ is None:  # conditioned by default
            try:
                building.properties.energy.set_all_room_2d_hvac(IdealAirSystem())
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed
        
        buildings.append(building)