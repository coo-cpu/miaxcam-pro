### Let's Design a Camera

1. 小孔成像，在物体和底片之间加一个小孔

   1. f = focal length
   2. c = center of the camera
   3. dimensionality reduction:3D ---- 2D
2. Single View Geometry(带有一些先验的观察)

   1. projection can be tricky.:相机把3D---2D，会有信息的丢失，如
      1. length is ***not*** preserved.
      2. angles are ***not*** preserved.
      3. straight lines are preserved.(铁轨) all lines converge to a vanishing point
         1. 所有的vanishing point 连成一条平行于成像平面的 vanishing line（也就是海天一线的那条线）
         2. 透视
         3. not all lines that interact are parallel.
         4. vertical vanishing points 存在于无限远（垂直于地面的直线依然垂直于地面）
      4. 镜头边缘的物体宽度会发生畸变，两边的物体会显得更宽
         1. 相机系统如果有一点角度偏移，就会产生很严重的畸变
3. What happens to a projection

   1. 为什么近大远小 （x, y, z）-----  (f*x/z, f* y/z)
   2. all points in the plane are at a fixed depth z
   3. ratios of lenghs and areas are preserved.
   4. 有的时候在制造的时候相机会存在制造上的误差，所以理论上会存在一些内外参需要校准
4. shrink the aperture

   1. 调小光圈会减小衍射，然唱歌航向更加清晰，但是也会导致成像更加暗。
5. Adding a lens(加一个镜头)

   1. 过去的小孔成像只吃一束光，但是加了透镜之后可以将很多束光汇聚在一个点（焦点，focal point）上
   2. 景深（depth of field 深了或者浅了都会模糊）
      1. 光圈大会模糊，光圈小会focus得比较好,增加了对焦范围，但是需要更大的进光量(见课件controlling depth of field.）
   3. 可以用两个相似三角形来计算（1/D + 1/D' = 1/f）
   4. Field of View(视场角)见课件----f和d决定你的angle（几何关系）
   5. vigneting（光晕）
   6. radical Distortion(畸变，直线变曲线)
   7. Chromatic Aberration：color fringing（复色光的不同颜色没有在像平面上面汇聚到同一点）
6. How light is recorded?

   1. CMOS & CCD
7. Image Formation

   1. surface reflectance properties(albedo, directional source, 表面法线（surface normal）)
   2. light source properties(Intensity, angle )
   3. exposure
   4. ...
8. Radiance(L) and Irradiance(E)
