# fluxmapPy &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ![alt text](https://www.atmofacts.com/_next/image?url=%2Fpub-images%2Ffull-color-logo-FINAL.png&w=384&q=75)

fluxmapPy is a python package that allows users to easily analyze FluxMaps. FluxMaps are spatialized eddy covariance rasters developed by AtmoFacts. fluxmapPy allows for users to visualize single bands of FluxMap rasters, filter out FluxMap raster pixels using a quality threshold, and compute diurnal cycles and spatial statistics for whole raster or within specific polygons. 

While there are multiple functions that allow for the analysis of FluxMaps, fluxmapPy offers 4 main wrapper functions that are described below. Additional functions that make up the wrapper functions, can be located in the API Reference tab. 

*Disclaimer - fluxmapPy is in early stages (0.6.0), so function names may change before the 1.0.0 release. Function name changes could break code.

<br><br><br>


### Additional Links

fluxmapPy tutorial:

Contributing:


<br><br><br>

## fluxmapPy License

Copyright (c) 2026 AtmoFacts, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<br><br><br>


<span style="font-size: 26px;">wrap_open_fm<span style="font-size: 22px;">(raster_path, &nbsp;&nbsp;&nbsp; qf_path = None,&nbsp;&nbsp;&nbsp; band = 0,&nbsp;&nbsp;&nbsp; qf_thsh = 4, &nbsp;&nbsp;&nbsp;qf_keep = 'lte'):
::: fluxmappy.wrap_open_fm.wrap_open_fm
<br><br><br>

<span style="font-size: 26px;">wrap_filt_qf<span style="font-size: 22px;">(data, &nbsp;&nbsp;&nbsp; flux = 'fluxCo2',&nbsp;&nbsp;&nbsp; qf_thsh = 4, &nbsp;&nbsp;&nbsp;qf_keep = 'lte'):
::: fluxmappy.wrap_filt_qf.wrap_filt_qf
<br><br><br>

<span style="font-size: 26px;">wrap_diu<span style="font-size: 22px;">(filtered_rasters, &nbsp;&nbsp;&nbsp; vector = None,&nbsp;&nbsp;&nbsp; in_tz = 'UTC', &nbsp;&nbsp;&nbsp; out_tz = 'None'):
::: fluxmappy.wrap_diu.wrap_diu
<br><br><br>

<span style="font-size: 26px;">wrap_stat<span style="font-size: 22px;">(filtered_rasters, &nbsp;&nbsp;&nbsp; vector = None,&nbsp;&nbsp;&nbsp; product = 'Daily')
::: fluxmappy.wrap_stat.wrap_stat
