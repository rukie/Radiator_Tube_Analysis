# Radiator Tube Analysis

This project is focused on the development of radiator tube technology and understanding. 
Open source tools are utilized to generate a variety of known industrial cad geometries. 
Open source tools are utilized to create a CFD mesh, and open source tools are utilized to study the fluid flow. 

The intent is to create a relevant repository on heat exchanger types and the accuracy of their
correlations against engineering principles. Some manufacturers claim significant increases in performance
over 'standard' designs, and this is an attempt to verify those claims.


# CAD Geometry

CadQuery is utilized to generate tubes of various shapes and sizes. 

Each tube type is populated with a type of turbulator.

Since tubes are paremeterized, various configurations are generated.

Nusselt numbers are calculated for each configuration.


Type List
* Circle
* Oval
* Rectangle
* Flat Oval Tube (Rounded Rectangle)


Turbulator Types
* None
* Square Nodules
* Ribs


Turbulator Pattern
* Recti-linear grid
* 30 degree
* 45 degree
* 60 degree

# Mesh

SnappyHexMesh



# Workflow

1. Geometry
   
   1. Use Python CadQuery
   
   2. Create tube
   
   3. Create turbulator
   
   4. Create negative space for CFD

2. Mesh
   
   1. Use SnappyHexMesh
   
   2. Scale STL if necessary (it is)
   
   3. Define inputs/outputs



# Results


