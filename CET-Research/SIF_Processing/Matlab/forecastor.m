function forecastor(imgFile, outfile, lightIntensity)
	% TODO: incorporate dt and measured lightIntensity into algorithm
	% and save the color bar as separate image
    
    img = imread(imgFile);
    % Take the complement of the image
    img = imcomplement(img);
    % Convert to gray
    img = rgb2gray(img);   
    % Create and save the colormap
    f = figure('visible','off','PaperPositionMode','auto');
    imshow(img, 'Border','tight');
    map = (lightIntensity/1024).*jet;
    colormap(map);
    saveas(f,outfile,'jpg');
    
end