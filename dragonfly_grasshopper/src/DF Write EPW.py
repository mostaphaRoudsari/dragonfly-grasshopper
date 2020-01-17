# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Write an EPW object into a .epw file.
-

    Args:
        _epw_obj: An EPW object such as that exported from the Create EPW
            component.
        _folder_: A directory into which the .epw file will be written.
        _file_name_: An optional name for the .epw file. Default will use the
            city of the EPW object's location.
        _run: Set to True to run the component and write the .epw file.
    
    Returns:
        report: Reports, errors, warnings, etc.
        epw_file: File path to a .epw that contains all of the data in the
            input _epw_obj.
"""

ghenv.Component.Name = "DF Write EPW"
ghenv.Component.NickName = 'WriteEPW'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '4 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os

try:
    from ladybug.epw import EPW
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    assert isinstance(_epw_obj, EPW), '_epw_obj must be an EPW object from the ' \
        'Create EPW component. Got {}.'.format(type(_epw_obj))
    
    # write out the epw object
    if _folder_ is None:
        _folder_ = os.path.join(os.environ['USERPROFILE'], 'ladybug')
    if _file_name_ is None:
        _file_name_ = _epw_obj.location.city
    if not _file_name_.endswith('.epw'):
        _file_name_ = _file_name_ + '.epw'
    
    epw_file = os.path.join(_folder_, _file_name_)
    _epw_obj.save(epw_file)