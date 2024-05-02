

from netCDF4 import Dataset
import argparse
import numpy as np
import os
import datetime
import pandas as pd


NODATA=-9999

def add_main_metadata(nc_ds):
    nc_ds.ncei_template_version = "NCEI_NetCDF_Swath_Template_v2.0"  
    nc_ds.summary = "The Earth Surface Mineral Dust Source Investigation (EMIT) is an Earth Ventures-Instrument (EVI-4) \
Mission that maps the surface mineralogy of arid dust source regions via imaging spectroscopy in the visible and \
short-wave infrared (VSWIR). Installed on the International Space Station (ISS), the EMIT instrument is a Dyson \
imaging spectrometer that uses contiguous spectroscopic measurements from 410 to 2450 nm to resolve absoprtion \
features of iron oxides, clays, sulfates, carbonates, and other dust-forming minerals. During its one-year mission, \
EMIT will observe the sunlit Earth's dust source regions that occur within +/-52° latitude and produce maps of the \
source regions that can be used to improve forecasts of the role of mineral dust in the radiative forcing \
(warming or cooling) of the atmosphere.\n"


    nc_ds.keywords = "Imaging Spectroscopy, minerals, EMIT, dust, radiative forcing"
    nc_ds.Conventions = "CF-1.63, ACDD-1.3"
    nc_ds.sensor = "EMIT (Earth Surface Mineral Dust Source Investigation)"
    nc_ds.instrument = "EMIT"
    nc_ds.platform = "ISS"

    # Feel free to modify institution
    nc_ds.institution = "NASA Jet Propulsion Laboratory/California Institute of Technology"
    nc_ds.license = "Freely Distributed"
    nc_ds.naming_authority = "LPDAAC"
    dt_now = datetime.utcnow()
    nc_ds.date_created = dt_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    nc_ds.keywords_vocabulary = "NASA Global Change Master Directory (GCMD) Science Keywords"
    nc_ds.stdname_vocabulary = "NetCDF Climate and Forecast (CF) Metadata Convention"

    # Feel free to modify
    nc_ds.creator_name = "Jet Propulsion Laboratory/California Institute of Technology"

    nc_ds.creator_url = "https://www.jpl.nasa.gov/"
    nc_ds.project = "Earth Surface Mineral Dust Source Investigation"
    nc_ds.project_url = "https://emit.jpl.nasa.gov/emit"
    nc_ds.publisher_name = "NASA LPDAAC"
    nc_ds.publisher_url = "https://lpdaac.usgs.gov"
    nc_ds.publisher_email = "lpdaac@usgs.gov"
    nc_ds.identifier_product_doi_authority = "https://doi.org"
    nc_ds.processing_level = "L4"
    
    nc_ds.geospatial_bounds_crs = "EPSG:4326"


    nc_ds.title = "EMIT L4 Earth System Model Products V001; "


def add_variable(nc_ds, nc_name, data_type, long_name, units, data, kargs):
    kargs['fill_value'] = NODATA

    nc_var = nc_ds.createVariable(nc_name, data_type, **kargs)
    if long_name is not None:
        nc_var.long_name = long_name
    if units is not None:
        nc_var.units = units

    if data_type is str:
        for _n in range(len(data)):
            nc_var[_n] = data[_n]
    else:
        nc_var[...] = data
    nc_ds.sync()


ACCEPTED_VARIABLES = [
    'input_mineral_fraction_emitted',
    'modeled_mineral_soil_emissions',
    'atmospheric_mineral_composition',
    'dust_shortwave_radiativeforcing_topofatmosphere',
    'dust_shortwave_radiativeforcing_surface',
    'dust_longwave_radiativeforcing_topofatmosphere',
    'dust_longwave_radiativeforcing_surface',
    'dust_aerosol_optical_depth_visible',
    'dust_single_scattering_albedo_visible',
    'dust_aerosol_optical_depth_550',
    'dust_single_scattering_albedo_550',
    'wet_deposition',
    'dry_deposition',
    'surface_concentration_by_volume',
]

ACCEPTED_MINERAL_NAMES = [
    'goethite',
    'hematite',
]


def main():
    parser = argparse.ArgumentParser(description='netcdf conversion')
    parser.add_argument('input_file', type=str)
    parser.add_argument('output_file', type=str)
    parser.add_argument('--dimensions', nargs=5, default=['bins','lon','lat','lev','time'])
    parser.add_argument('--use_dimensions', nargs=5, default=[1,1,1,1,1])
    parser.add_argument('--l4_naming_file', default='data/l4_naming.csv')
    args = parser.parse_args()

    l4_naming = pd.read_csv(args.l4_naming_file)

    source_dataset = Dataset(args.input_file, 'r')


    nc_ds = Dataset(os.path.splitext(args.output_file)[0] + '.nc', 'w', clobber=True, format='NETCDF4')

    #TODO Add your high level sumary information for the specific model here - we'll automatically fill in per variable later:
    #nc_ds.summary += "This model is the XXXX and works like XXXX"

    #nc_ds.input_description += "This is how this model went from EMIT L3 to the specified input"
    nc_ds.sync()

    out_dimension_names = ['bins','lon','lat','lev','time']
    out_dimensions = [out_dimension_names[n] for n in range(len(out_dimension_names)) if args.use_dimensions[n]]

    for n in range(len(out_dimension_names)):
        if args.use_dimensions[n]:
            nc_ds.createDimension(out_dimension_names[n], source_dataset.dimensions[args.dimensions[n]].size)

    potential_name_combinations = ACCEPTED_MINERAL_NAMES.copy()
    for varname in l4_naming['Long Name']:
        for mineral_name in ACCEPTED_MINERAL_NAMES:
            potential_name_combinations.append(varname + "_" + mineral_name)

    for varname in list(source_dataset.variables):
        if varname not in potential_name_combinations:
            nc_ds.close()
            raise ValueError("Variable name not recognized as consistent with standardized names: " + varname)
        add_variable(nc_ds, varname, "f4", varname, None, source_dataset.variables[varname][:], {"dimensions": tuple(out_dimensions)})

        nc_ds.title += varname
        for _vn, vn in enumerate(l4_naming['Long Name']):
            if vn in varname:
                nc_ds.summary += '\n' + l4_naming['Description'][_vn]
                break

    nc_ds.sync()
    nc_ds.close()




if __name__ == "__main__":
    main()
