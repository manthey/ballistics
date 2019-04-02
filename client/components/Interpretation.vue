<template>
  <div id="computation" class="textblock">
    <vue-markdown>
# Interpretation

The goal of this study is determine how the quality of powder varied over time.  The available data includes accuracte and inaccurate results, and contains much variation.  This variation is due to environmental conditions, measurement precision, transcription errors, measurement technique, reporting thoroughness, computation model, and other factors.  Different views of the data can help or obscure seeing true trends.

## [Full Data](#/plot)

All the data.

## [Preferred Techniques](#/plot?filter={{ filters.preferred }})

Only techniques that are more likely to be accurate.  This excludes `theory` as it isn't actual measurements, `time` and `final_angle` as they tend to be very low accuracy, and `calorimeter` as this doesn't measure realized ballistic force.

## Box Plot

A box plot is a common statistical method to show the median, quartiles, and outliers.  This can be used to aggregate data over a periods of time.  Using the preferred techniques and 25-year interval aggregation, there appears to be a distinct trend.  This trend is less obvious with 20 or 10 year intervals.

- [Box Plot, Full Data, 25 year intervals](#/boxplot)
- [Box Plot, Preferred Technique, 25 year intervals](#/boxplot?filter={{ filters.preferred }})
- [Box Plot, Preferred Technique, 20 year intervals](#/boxplot?filter={{ filters.preferred }}&binwidth=20)
- [Box Plot, Preferred Technique, 10 year intervals](#/boxplot?filter={{ filters.preferred }}&binwidth=10)

## Median and Quartile Values

Instead of aggregating all data into box plots, the median or quartile points can be plotted.  These can be separated by data source and technique, and can also be aggregated by year or a span of years.

- [Median Values by Source, Technique, and Year](#/plot?filter={{ filters.median_source_technique_year }})
- [Third Quartile Values by Source, Technique, and Year](#/plot?filter={{ filters.quartile_source_technique_year }})
- [Third Quartile Values by Source, Technique, and 10 year intervals](#/plot?filter={{ filters.quartile_source_technique_10year }})
- [Third Quartile Values by Source, Technique, and 20 year intervals](#/plot?filter={{ filters.quartile_source_technique_20year }})
- [Third Quartile Values by Source, Technique, and 25 year intervals](#/plot?filter={{ filters.quartile_source_technique_25year }})
- [Third Quartile Values by Technique and Year](#/plot?filter={{ filters.quartile_technique_year }})
- [Third Quartile Values by Technique and 10 year intervals](#/plot?filter={{ filters.quartile_technique_10year }})
- [Third Quartile Values by Technique and 20 year intervals](#/plot?filter={{ filters.quartile_technique_20year }})
- [Third Quartile Values by Technique and 25 year intervals](#/plot?filter={{ filters.quartile_technique_25year }})
    </vue-markdown>
  </div>
</template>

<style src="./textblock.css" scoped/>

<script>
import * as utils from '../utils.js';

export default {
  name: 'Interpretation',
  data() {
    var filters = {};
    Object.keys(utils.CommonFilters).map((key) => {
      filters[key] = utils.encodeFilter(utils.CommonFilters[key]);
    });
    return {
      filters: filters
    }
  }
}
</script>
