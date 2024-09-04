clear all
close all


% Base filename components

baseFilename = 'Basler_acA3088-57um__24919761__20240629_152640066_';
fileExtension = '.bmp';

% Range of numbers in the filenames
startNum = 316;
endNum = 2000;

% Define the output directory
outputDir_Polar = '../results/Polar2';
outputDir_XY = '../results/XY2';

% Create the output directory if it doesn't exist
if ~exist(outputDir_Polar, 'dir')
    mkdir(outputDir_Polar);
end

% Create the output directory if it doesn't exist
if ~exist(outputDir_XY, 'dir')
    mkdir(outputDir_XY);
end

lenMat = endNum-startNum+1;

centerMat = zeros(lenMat,2);
radiiMat = zeros(lenMat,1);
k = startNum



%% Loop through the range
for k = k:endNum
    % Generate the filename
    currentFilename = sprintf('%s%04d%s', baseFilename, k, fileExtension);
    
    % Read the image
    grayImg = imread(currentFilename);
    
    % Process the image (e.g., detect circle, convert to r-theta image, etc.)
    % For example, you can call the circle detection and transformation function here
    
    % Convert the image to grayscale

    % Adjust image contrast (optional, may help with detection)
    adjustedImg = imadjust(grayImg);

    % Define the range of radii to search for circles
    minRadius = 200; % Minimum radius of the circle
    maxRadius = 230; % Maximum radius of the circle

    % Detect circles
    [centers, radii, metric] = imfindcircles(~adjustedImg, [minRadius maxRadius], 'Sensitivity', 0.99);
    %
    if size(centers,1)>1
            centerMat(k-startNum+1,:) = centerMat(k-1,:);
            radiiMat(k-startNum+1) = radiiMat(k-1);
            
    else
            k
            centerMat(k-startNum+1,:) = centers;
            radiiMat(k-startNum+1) = radii;

    end
    
    %
    if ~isempty(centers) 
        % Assuming the first detected circle is the one we want


        % Define the number of angular and radial divisions
        numTheta = 360; % Number of angular divisions
        numR = radii; % Number of radial divisions

        % Create a grid of theta and r values
        theta = linspace(0, 2*pi, numTheta);
        extraRadii=40;
        %r = linspace(0, radii+extraRadii, numR+extraRadii);
        TrueRadii=215+extraRadii;
        r = linspace(0, TrueRadii, TrueRadii);
       
        [Theta, R] = meshgrid(theta, r);

        % Convert polar coordinates to Cartesian coordinates
        X = R .* cos(Theta) + centers(1);
        Y = R .* sin(Theta) + centers(2);

        % Interpolate pixel values at these coordinates
        polarImg = interp2(double(grayImg), X, Y);

        % Convert polar image to uint8 for saving
        polarImgUint8 = uint8(polarImg);

        outputFilename = fullfile(outputDir_Polar, sprintf('polar_%04d.png', k));
        % Save the polar image
        imwrite(polarImgUint8, outputFilename);
        
        % Define the bounding box for cropping
        radius = TrueRadii;
        xMin = max(1, round(centers(1) - radius));
        xMax = min(size(grayImg, 2), round(centers(1) + radius));
        yMin = max(1, round(centers(2) - radius));
        yMax = min(size(grayImg, 1), round(centers(2) + radius));

        % Crop the image
        grayImg_cropped = grayImg(yMin:yMax, xMin:xMax);
        outputFilenameXY= fullfile(outputDir_XY,sprintf('XY_%04d.png',k));
        imwrite(grayImg_cropped, outputFilenameXY);
        
        else
            disp(['No circles detected in ', currentFilename]);
        end

end

disp('Polar images saved to the "results/1" folder.');
