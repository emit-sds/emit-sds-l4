<h1 align="center"> emit-sds-l4 </h1>

Welcome to the EMIT Science Data System Level 4 repository.  This page holds reference material and conversions scripts in support of the Earth System Model runs made in support of EMIT. 


Each delivered granule consists of a series of output variables that are the product of a single model run.  The [models](https://github.com/emit-sds/emit-sds-l4/blob/main/data/models.csv) table  provides links to each granule, along with the parameters used to define that model run, including which model was run, what resolution the model was run at, the source input minerology, the external meteorology used (if used), the time period the run was for, and what emissions / concentration scenario was used.  The individual variables published with each dataset are listed [in the variable names table]](https://github.com/emit-sds/emit-sds-l4/blob/main/data/L4_varnames.csv) For additional information including documentation, data links, citation information, and related products, and more, please see the [EMIT L4 product landing page](https://lpdaac.usgs.gov/products/emitl4esmv001/). 


The current model table is:



Granule Name|ESM|Resolution|External Meteorology|Input Minerology|Time Period|Emissions/concentration scenario|Vegetation for emission source mask
|----------|----|----------|--------------------|----------------|----------|---------------------------------|--|
EMIT_L4_ESM_001_CESM_1.0-1.25-32_EMIT002-B_NONE_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 32|None|EMIT002 Baseline|2007-2011|Historical|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-32_EMIT002-B_NONE_2090-2094_SSP2-4.5|CESM 2.0-CAM6|1.0 x 1.25 x 32|None|EMIT002 Baseline|2090-2094|SSP2-4.5|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-32_EMIT002-B_NONE_2090-2094_SSP5-8.5|CESM 2.0-CAM6|1.0 x 1.25 x 32|None|EMIT002 Baseline|2090-2094|SSP5-8.5|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-56_EMIT002-B_MERRA2_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 56|MERRA2|EMIT002 Baseline|2007-2011|Historical|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-32_C1999-B_NONE_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 32|None|Claquin et al. 1999 Baseline|2007-2011|Historical|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-32_C1999-B_NONE_2090-2094_SSP2-4.5|CESM 2.0-CAM6|1.0 x 1.25 x 32|None|Claquin et al. 1999 Baseline|2090-2094|SSP2-4.5|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-32_C1999-B_NONE_2090-2094_SSP5-8.5|CESM 2.0-CAM6|1.0 x 1.25 x 32|None|Claquin et al. 1999 Baseline|2090-2094|SSP5-8.5|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-56_C1999-B_MERRA2_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 56|MERRA2|Claquin et al. 1999 Baseline|2007-2011|Historical|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-56_C1999-HC_MERRA2_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 56|MERRA2|Claquin et al. 1999 High Hematite Clay|2007-2011|Historical|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-56_C1999-HS_MERRA2_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 56|MERRA2|Claquin et al. 1999 High Hematite Silt|2007-2011|Historical|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-56_C1999-LC_MERRA2_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 56|MERRA2|Claquin et al. 1999 Low Hematite Clay|2007-2011|Historical|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-56_C1999-LS_MERRA2_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 56|MERRA2|Claquin et al. 1999 Low Hematite Silt|2007-2011|Historical|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-56_EMIT002-H_MERRA2_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 56|MERRA2|EMIT002 High Hematite|2007-2011|Historical|NA
EMIT_L4_ESM_001_CESM_1.0-1.25-56_EMIT002-L_MERRA2_2007-2011_HISTORICAL|CESM 2.0-CAM6|1.0 x 1.25 x 56|MERRA2|EMIT002 Low Hematite|2007-2011|Historical|NA
EMIT_L4_ESM_001_GISS_2.0-2.5-40_EMIT002-B_MERRA2_2007-2011_HISTORICAL-A|GISS ModelE2.1|2.0 x 2.5 x 40|MERRA2|EMIT002 Baseline|2007-2011|Historical|AVHRR
EMIT_L4_ESM_001_GISS_2.0-2.5-40_C1999-B_MERRA2_2007-2011_HISTORICAL-A|GISS ModelE2.1|2.0 x 2.5 x 40|MERRA2|Claquin et al. 1999 Baseline|2007-2011|Historical|AVHRR
EMIT_L4_ESM_001_GISS_2.0-2.5-40_EMIT002-L_MERRA2_2007-2011_HISTORICAL-A|GISS ModelE2.1|2.0 x 2.5 x 40|MERRA2|EMIT002 Low Iron Oxide|2007-2011|Historical|AVHRR
EMIT_L4_ESM_001_GISS_2.0-2.5-40_EMIT002-H_MERRA2_2007-2011_HISTORICAL-A|GISS ModelE2.1|2.0 x 2.5 x 40|MERRA2|EMIT002 High Iron Oxide|2007-2011|Historical|AVHRR
EMIT_L4_ESM_001_GISS_2.0-2.5-40_EMIT002-B_NONE_2007-2011_HISTORICAL-A|GISS ModelE2.1|2.0 x 2.5 x 40|None|EMIT002 Baseline|2007-2011|Historical|AVHRR




