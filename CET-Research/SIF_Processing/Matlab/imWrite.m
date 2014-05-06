%A = [200,200];
%count = 0;
%for x = 1:200
%    for y = 1:400
%        A(x,y) = count;
%        count = count + 0.001;
%    end
%end

%imwrite(A,'newImage.jpg','jpg','Comment','My JPEG file')

% Read input image
img = imread('cloudysky.jpg');
% Take the complement of the image
%img = imcomplement(img);
% Convert to gray
img = rgb2gray(img);
% Create and save the colormap to outfile
f = figure('visible','off','PaperPositionMode','auto');
imshow(img, 'Border','tight');
map = (900/1024).*jet;
colormap(map);
saveas(f,'lolimage2','jpg');