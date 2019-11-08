# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate relative humidity from Dry Bulb Temperature and Dew Point Temperature.
-

    Args:
        _dry_bulb: A value or data collection representing dry bulb temperature [C]
        _dew_point: A value or data collection representing dew point temperature [C]
    
    Returns:
        rel_humid: A data collection or value indicating the relative humidity [%]
"""

ghenv.Component.Name = "DF Relative Humidity from Dew Point"
ghenv.Component.NickName = 'RelHumid'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = '03 :: AlternativeWeather'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:
    from ladybug.psychrometrics import rel_humid_from_db_dpt
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.datatype.fraction import RelativeHumidity
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _dry_bulb and _dew_point:
    rel_humid = HourlyContinuousCollection.compute_function_aligned(
        rel_humid_from_db_dpt, [_dry_bulb, _dew_point], RelativeHumidity(), '%')