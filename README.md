# Radiator Tube Analysis

This project is focused on the development of radiator tube technology and understanding. Open source tools are utilized to generate a variety of known industrial cad geometries. Open source tools are utilized to create a CFD mesh, and open source tools are utilized to study the fluid flow. 



# CAD Geometry

CadQuery is utilized to generate tubes of various shapes and sizes. 



Type List

Rectangle

Flat Oval Tube (Rounded Rectangle)



Turbulator Types

Square Nodules

Ribs



Turbulator Pattern



# Mesh





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


