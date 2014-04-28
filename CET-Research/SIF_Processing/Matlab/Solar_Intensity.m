function Solar_Intensity(imgFile, outfile, lightIntensity)
im_out = imread(imgFile);
% Take the complement of the image
im_out = imcomplement(im_out);
% Convert to gray
im_out = rgb2gray(im_out);
% Create and save the colormap to outfile
f = figure('visible','off','PaperPositionMode','auto');
imshow(im_out, 'Border','tight');
map = (900/1024).*jet;
colormap(map);
saveas(f,outfile,'jpg');
end