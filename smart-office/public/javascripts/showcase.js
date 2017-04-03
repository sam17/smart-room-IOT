// Color pickers in different flavors.
// -----------------------------------

var cpDefault = ColorPicker(document.getElementById('default'), updateInputs);

// Inputs.
// -------

var iR = document.getElementById('rgb_r');
var iG = document.getElementById('rgb_g');
var iB = document.getElementById('rgb_b');

var rgbCSS = document.getElementById('rgb_css');
var hsvCSS = document.getElementById('hsv_css');

var color = document.getElementById('color');
var textColor = document.getElementById('text-color');

function updateInputs(hex) {
    setColor(hex);
    var rgb = ColorPicker.hex2rgb(hex);
    var hsv = ColorPicker.hex2hsv(hex);
    
    iR.value = rgb.r;
    iG.value = rgb.g;
    iB.value = rgb.b;
    
    color.style.backgroundColor = hex;
}

function updateColorPickers(hex) {
    cpDefault.setHex(hex);
}

var initialHex = '#f4329c';
updateColorPickers(initialHex);

function setColor(hex) {
    var rgb = ColorPicker.hex2rgb(hex);
    var ip = "localhost";
    var url = "http://"+ip+"/"+rgb.r+"/"+rgb.g+"/"+rgb.b+"/";
    $.get(url, function(data, status){
        console.log("Data: " + data + "\nStatus: " + status);
    });
}

iR.onchange = function() { updateColorPickers(ColorPicker.rgb2hex({ r: iR.value, g: iG.value, b: iB.value })); }
iG.onchange = function() { updateColorPickers(ColorPicker.rgb2hex({ r: iR.value, g: iG.value, b: iB.value })); }
iB.onchange = function() { updateColorPickers(ColorPicker.rgb2hex({ r: iR.value, g: iG.value, b: iB.value })); }