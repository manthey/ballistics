/* General utility values and functions */

import math from 'mathjs';

let memoizeCompare = {_count: 0, _maxcount: 1000};
let memoizeFormatValue = {_count: 0, _maxcount: 10000};

/* Default mathjs number format. */
let NumberFormat = {precision: 6, lowerExp: -6, upperExp: 9};

/* Sorted list of known parameters and their formats. */
let ParameterList = [{
    key: 'ref',
    primary: true
  }, {
    key: 'key',
    primary: true
  }, {
    key: 'idx',
    title: '0-based location in the data file',
    primary: true
  }, {
    key: 'sourceline',
    title: '1-based line number in the data file',
    primary: true
  }, {
    key: 'desc',
    primary: true
  }, {
    key: 'date',
    primary: true
  }, {
    key: 'date_filled'
  }, {
    key: 'year'
  }, {
    key: 'technique',
    primary: true
  }, {
    key: 'power_factor',
    units: 'J/kg',
    primary: true
  }, {
    key: 'given_date',
    primary: true
  }, {
    key: 'given_date_note'
  }, {
    key: 'given_power_factor',
    primary: true
  }, {
    key: 'given_power_factor_note',
  }, {
    key: 'given_charge',
    primary: true
  }, {
    key: 'given_charge_note'
  }, {
    key: 'given_diameter',
    primary: true
  }, {
    key: 'given_diameter_note'
  }, {
    key: 'given_angle',
    primary: true
  }, {
    key: 'given_angle_note'
  }, {
    key: 'given_range',
    primary: true
  }, {
    key: 'given_range_note'
  }, {
    key: 'given_final_angle',
    primary: true
  }, {
    key: 'given_final_height',
    primary: true
  }, {
    key: 'given_final_height_note'
  }, {
    key: 'given_final_time',
    primary: true
  }, {
    key: 'given_final_time_note'
  }, {
    key: 'given_final_velocity',
    primary: true
  }, {
    key: 'given_final_velocity_note',
  }, {
    key: 'given_pendulum_impact_length',
    primary: true
  }, {
    key: 'given_pendulum_impact_mass',
    title: 'Weight of previously fired projectiles.',
    primary: true
  }, {
    key: 'given_pendulum_impact_mass_note',
  }, {
    key: 'given_pendulum_index_chord',
    primary: true
  }, {
    key: 'given_pendulum_index_length',
    primary: true
  }, {
    key: 'given_pendulum_index_length_note',
  }, {
    key: 'given_pendulum_index_angle',
    primary: true
  }, {
    key: 'given_pendulum_mass',
    primary: true
  }, {
    key: 'given_pendulum_mass_note',
  }, {
    key: 'given_pendulum_mass_length',
    primary: true
  }, {
    key: 'given_pendulum_mass_length_note'
  }, {
    key: 'given_pendulum_period',
    primary: true
  }, {
    key: 'given_pendulum_period_note',
  }, {
    key: 'given_atmospheric_density',
    primary: true
  }, {
    key: 'given_atmospheric_density_note'
  }, {
    key: 'given_group',
    primary: true
  }, {
    key: 'given_temperature',
    primary: true
  }, {
    key: 'given_temperature_note'
  }, {
    key: 'given_humidity',
    primary: true
  }, {
    key: 'given_humidity_note'
  }, {
    key: 'given_wetbulb',
    primary: true
  }, {
    key: 'given_initial_height',
    primary: true
  }, {
    key: 'given_initial_height_note'
  }, {
    key: 'given_initial_velocity',
    primary: true
  }, {
    key: 'given_initial_velocity_note'
  }, {
    key: 'given_mass',
    primary: true
  }, {
    key: 'given_mass_note'
  }, {
    key: 'given_material',
    primary: true
  }, {
    key: 'given_material_note'
  }, {
    key: 'given_material_density',
    primary: true
  }, {
    key: 'given_maxheight',
    primary: true
  }, {
    key: 'given_maxheight_note'
  }, {
    key: 'given_pressure',
    primary: true
  }, {
    key: 'given_rising_height',
    primary: true
  }, {
    key: 'given_chamber_volume',
    title: 'Volume of pressure chamber',
    primary: true
  }, {
    key: 'given_chamber_diameter',
    title: 'Diameter of pressure chamber measurement area',
    primary: true
  }, {
    key: 'given_delta_range',
    title: 'Difference in range between two time measurements.',
    primary: true
  }, {
    key: 'given_delta_time',
    title: 'Difference in time between two range measurements.',
    primary: true
  }, {
    key: 'given_delta_time_note',
  }, {
    key: 'given_technique',
    primary: true
  }, {
    key: 'given_technique_note'
  }, {
    key: 'charge',
    units: 'kg',
    primary: true
  }, {
    key: 'diam',
    units: 'm',
    primary: true
  }, {
    key: 'range',
    units: 'm',
    primary: true
  }, {
    key: 'final_angle',
    units: 'deg',
    primary: true
  }, {
    key: 'final_height',
    units: 'm',
    primary: true
  }, {
    key: 'final_time',
    units: 's',
    primary: true
  }, {
    key: 'final_velocity',
    units: 'm/s',
    primary: true
  }, {
    key: 'pendulum_impact_length',
    units: 'm',
    primary: true
  }, {
    key: 'pendulum_impact_mass',
    units: 'kg',
    primary: true
  }, {
    key: 'pendulum_index_chord',
    units: 'm',
    primary: true
  }, {
    key: 'pendulum_index_length',
    units: 'm',
    primary: true
  }, {
    key: 'pendulum_index_angle',
    units: 'deg',
    primary: true
  }, {
    key: 'pendulum_mass',
    units: 'kg',
    primary: true
  }, {
    key: 'pendulum_mass_length',
    units: 'm',
    primary: true
  }, {
    key: 'pendulum_period',
    units: 's',
    primary: true
  }, {
    key: 'atmospheric_density',
    units: 'kg/m^3',
    primary: true
  }, {
    key: 'rh',
    primary: true
  }, {
    key: 'initial_height',
    units: 'm',
    primary: true
  }, {
    key: 'initial_velocity',
    units: 'm/s',
    primary: true
  }, {
    key: 'mass',
    units: 'kg',
    primary: true
  }, {
    key: 'material',
    primary: true
  }, {
    key: 'material_density',
    units: 'kg/m^3',
    primary: true
  }, {
    key: 'projectile_density',
    units: 'kg/m^3',
    primary: true
  }, {
    key: 'max_height',
    units: 'm',
    primary: true
  }, {
    key: 'pressure',
    units: 'Pa',
    primary: true
  }, {
    key: 'pressure_y0',
    units: 'm',
    primary: true
  }, {
    key: 'rising_height',
    units: 'm',
    primary: true
  }, {
    key: 'chamber_volume',
    title: 'Volume of pressure chamber',
    units: 'm^3',
    primary: true
  }, {
    key: 'chamber_diameter',
    title: 'Diameter of pressure chamber measurement area',
    units: 'm',
    primary: true
  }, {
    key: 'delta_range',
    title: 'Difference in range between two time measurements.',
    units: 'm',
    primary: true
  }, {
    key: 'delta_time',
    title: 'Difference in time between two range measurements.',
    units: 's',
    primary: true
  }, {
    key: 'computation_time',
    units: 's'
  }, {
    key: 'initial_angle',
    units: 'deg'
  }, {
    key: 'T',
    title: 'Air temperature',
    units: 'K'
  }, {
    key: 'Twb',
    title: 'Wet-bulb temperature',
    units: 'K'
  }, {
    key: 'time',
    units: 's'
  }, {
    key: 'x',
    units: 'm'
  }, {
    key: 'y',
    units: 'm'
  }, {
    key: 'vx',
    units: 'm/s'
  }, {
    key: 'vy',
    units: 'm/s'
  }, {
    key: 'ax',
    units: 'm/s^2'
  }, {
    key: 'ay',
    units: 'm/s^2'
  }, {
    key: 'final_density_density',
    units: 'kg/m^3'
  }, {
    key: 'final_density_h',
    title: 'final density humidity (0-1)'
  }, {
    key: 'final_density_pressure',
    units: 'Pa'
  }, {
    key: 'final_density_psv',
    title: 'Vapor pressure at saturation',
    units: 'Pa'
  }, {
    key: 'final_density_T',
    units: 'K'
  }, {
    key: 'final_density_xv',
  }, {
    key: 'final_density_y',
    units: 'm'
  }, {
    key: 'final_drag_cd'
  }, {
    key: 'final_drag_Mn'
  }, {
    key: 'final_drag_Re'
  }, {
    key: 'final_drag_critical_Re'
  }, {
    key: 'final_drag_sos',
    units: 'm/s'
  }, {
    key: 'final_drag_in_range'
  }, {
    key: 'final_viscosity_mua',
    title: 'Viscosity of dry air',
    units: 'kg/m/s'
  }, {
    key: 'final_viscosity_muv',
    title: 'Viscosity of water vapor',
    units: 'kg/m/s'
  }, {
    key: 'final_viscosity_viscosity',
    title: 'Viscosity',
    units: 'kg/m/s'
  }, {
    key: 'time_delta',
    units: 's'
  }, {
    key: 'version',
  }];
let Parameters = {};
ParameterList.forEach((param, idx) => {
  param.idx = idx;
  Parameters[param.key] = param;
});

let PointKeys = {};

let medianPreamble = "((d, data) => {" +
  "if (['height','time','theory','calorimeter','final_angle'].indexOf(d.technique)>=0) return false;" +
  "if (!d.dkey) data.forEach(d => {";
let medianBin = "}); if (!data.sets) data.sets={}; var set = data.sets[d.dkey]; if (!set) data.sets[d.dkey] = data.filter(e => d.dkey === e.dkey).sort((a, b) => a.power_factor - b.power_factor); set = data.sets[d.dkey];  return d === set[Math.floor((set.length-1) * ";
let medianPost = ")]; })(d, data)";

let CommonFilters = {
  preferred: "['time','theory','calorimeter','final_angle'].indexOf(d.technique)<0",
  preferred_solid: "['time','theory','calorimeter','final_angle'].indexOf(d.technique)<0 && d.projectile_density>6800",
  preferred_small: "['time','theory','calorimeter','final_angle'].indexOf(d.technique)<0 && d.diam<0.0255",
  preferred_large: "['time','theory','calorimeter','final_angle'].indexOf(d.technique)<0 && d.diam>0.0253",
  median_source_technique_year: medianPreamble +
    "d.dkey = d.key+':'+d.technique+':'+d.year;" +
    medianBin + "0.5" + medianPost,
  quartile_source_technique_year: medianPreamble +
    "d.dkey = d.key+':'+d.technique+':'+d.year;" +
    medianBin + "0.75" + medianPost,
  quartile_source_technique_10year: medianPreamble +
    "d.dkey = d.key+':'+d.technique+':'+Math.floor(d.year/10);" +
    medianBin + "0.75" + medianPost,
  quartile_source_technique_20year: medianPreamble +
    "d.dkey = d.key+':'+d.technique+':'+Math.floor(d.year/20);" +
    medianBin + "0.75" + medianPost,
  quartile_source_technique_25year: medianPreamble +
    "d.dkey = d.key+':'+d.technique+':'+Math.floor(d.year/25);" +
    medianBin + "0.75" + medianPost,
  quartile_technique_year: medianPreamble +
    "d.dkey = d.technique+':'+d.year;" +
    medianBin + "0.75" + medianPost,
  quartile_technique_10year: medianPreamble +
    "d.dkey = d.technique+':'+Math.floor(d.year/10);" +
    medianBin + "0.75" + medianPost,
  quartile_technique_20year: medianPreamble +
    "d.dkey = d.technique+':'+Math.floor(d.year/20);" +
    medianBin + "0.75" + medianPost,
  quartile_technique_25year: medianPreamble +
    "d.dkey = d.technique+':'+Math.floor(d.year/25);" +
    medianBin + "0.75" + medianPost
};

/**
 * Since we use filters in markdown, we have URI encode them and escape
 * parentheses.
 *
 * @param {string} value A string to encode.
 * @returns {string} The encoded string.
 */
function encodeFilter(val) {
  val = encodeURIComponent(val);
  val = val.replace(/\(/g, '%28').replace(/\)/g, '%29');
  return val;
}

/**
 * Filter data based on user input.  See
 * https://stackoverflow.com/questions/47444376 for sanitization rationale.
 *
 * Enter: data: the data to filter.
 *        filter: the filter string.
 * Exit:  data: the filtered data.
 */
function filterData(data, filter) {
  try {
    let args = ['d', 'i', 'data'].concat(Object.keys(window));
    args = args.filter(key => /^[a-zA-Z_$][0-9a-zA-Z_$]*$/.exec(key));
    args.push('"use strict";return(' + filter + ')');
    let filterFunc = Function.apply(null, args);
    data = data.map(d => Object.assign({}, d));
    return data.filter((d, i, data) => filterFunc.call({}, d, i, data));
  } catch (err) {
    console.error('Filter failed: ' + this.filter);
    console.error(err);
    return data;
  }
}

/**
 * Given a value and a parameter specification, format the value either as text
 * or as a number, possibly with units.
 *
 * @param {string|number} value The value to format.
 * @param {object} params An entry from Parameters.
 * @returns {string} The formatted value.
 */
function formatValue(value, params) {
  let key = ((params && params.key) || 'none'), result;
  if (key in memoizeFormatValue && value in memoizeFormatValue[key]) {
    return memoizeFormatValue[key][value];
  }
  if (isNaN(+value)) {
    result = value;
  } else if (params && params.units) {
    result = math.unit(+value, params.units).format(NumberFormat);
  } else {
    result = math.format(+value, NumberFormat);
  }
  if (memoizeFormatValue._count > memoizeFormatValue._maxcount) {
    memoizeFormatValue = {_count: 0, _maxcount: memoizeFormatValue._maxcount};
  }
  if (!(key in memoizeFormatValue)) {
    memoizeFormatValue[key] = {};
  }
  memoizeFormatValue[key][value] = result;
  memoizeFormatValue._count += 1;
  return result;
}

/**
 * Sort a list of objects.  This does not mutate the original list, but does
 * add a rowidx property to each object.
 *
 * @param {array} objectList The list to sort.
 * @param {array} sortOrder A list of sort actions, the end ones are most
 *   significant.  Each entry is {prop: <key>, order: 'ascending'|'descending'}
 *   where order defaults to ascending.  A key of "pointkey" is special; it is
 *   shorthand for [{prop: 'key'}, {prop: 'idx'}], both with the same order.
 * @returns {array} The sorted list.
 */
function sortObjectList(objectList, sortOrder) {
  let sortedList = objectList.slice().sort((a, b) => {
    let i, o, key, dir;
    for (i = sortOrder.length - 1; i >= 0; i--) {
      key = sortOrder[i].prop;
      dir = sortOrder[i].order !== 'descending';
      if (key === 'pointkey') {
        return dir ? (a.key > b.key ? 1 : a.key < b.key ? -1 : a.idx - b.idx) : (a.key > b.key ? -1 : a.key < b.key ? 1 : b.idx - a.idx);
      }
      if (a[key] === b[key]) {
        continue;
      }
      if (a[key] === undefined) {
        return dir ? -1 : 1;
      }
      if (b[key] === undefined) {
        return dir ? 1 : -1;
      }
      const an = +a[key], bn = +b[key];
      if (!isNaN(an) && !isNaN(bn)) {
        if (an === bn) {
          continue;
        }
        return dir ? an - bn : bn - an;
      }
      const astr = ''+a[key], bstr = ''+b[key];
      if (astr === bstr) {
        continue;
      }
      if (astr in memoizeCompare && bstr in memoizeCompare[astr]) {
        o = memoizeCompare[astr][bstr];
      } else {
        o = astr.localeCompare(bstr, undefined, {ignorePunctuation: true});
        if (memoizeCompare._count > memoizeCompare._maxcount) {
          memoizeCompare = {_count: 0, _maxcount: memoizeCompare._maxcount};
        }
        if (!(astr in memoizeCompare)) {
          memoizeCompare[astr] = {};
        }
        memoizeCompare[astr][bstr] = o;
        memoizeCompare._count += 1;
      }
      if (o) {
        return dir ? o : -o;
      }
    }
    return 0;
  });
  sortedList.forEach((entry, idx) => { entry.rowidx = idx; });
  return sortedList;
}

/**
 * Given information about parameters in the total data list, update the
 * ParameterList and Parameters records.  Emit console messages if there are
 * parameters present in one set and not the other.
 *
 * @param {object} params A dictionary of parameter information from the data.
 * @returns {object} The updates Parameters value.
 */
function updateParameters(params) {
  Object.keys(Parameters).forEach(key => {
    if (!params[key]) {
      console.log(`The client Parameters include ${key}, but it is missing in the data.`);
    }
  });
  Object.keys(params).forEach(key => {
    if (!Parameters[key]) {
      console.log(`The data parameters include ${key}, but it is missing in the client.`);
      Parameters[key] = {'key': key};
      ParameterList.push(Parameters[key]);
    }
    Object.assign(Parameters[key], params[key]);
  });
  return Parameters;
}

/**
 * Given the main data, fill a dictionary of keys with references to the data
 * points.  This also populates formatted values for the data points.
 *
 * @param {object} data The main data.
 * @returns {object} The updates PointKeys dictionary.
 */
function updatePointKeys(data) {
  data.forEach(entry => {
    let pointkey = entry.key + '-' + entry.idx;
    Object.keys(entry).forEach(key => {
      if (!key.startsWith('_')) {
        let fvalue = formatValue(entry[key], Parameters[key]);
        if (fvalue !== entry[key]) {
          entry['_' + key] = fvalue;
        }
      }
    });
    PointKeys[pointkey] = entry;
    entry.pointkey = pointkey;
  });
  return PointKeys;
}

export {
  CommonFilters,
  NumberFormat,
  ParameterList,
  Parameters,
  PointKeys,

  encodeFilter,
  filterData,
  formatValue,
  sortObjectList,
  updateParameters,
  updatePointKeys
};
