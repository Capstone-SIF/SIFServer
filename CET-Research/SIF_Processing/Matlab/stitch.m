function stitch(imgDir)


D = dir (fullfile(imgDir, '*_1_*.jpg'));
F = dir (fullfile(imgDir, '*_2_*.jpg'));



%clear imCell;
imCell1 = cell(1,numel(D));

for i = 1:numel(D)
imCell1{i} = imread(D(i).name);
end

imCell2 = cell(1,numel(F));

for i = 1:numel(F)
imCell2{i} = imread(F(i).name);
end


sift_mosaic(imCell1{1}, imCell1{2});
sift_mosaic2(imCell2{1}, imCell2{2});
end
