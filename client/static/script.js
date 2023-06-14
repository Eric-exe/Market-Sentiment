let recColors = ["#008f88", "#00c073", "#ffdc48", "#ffa33e", "#ff0000"];

let sentColors = ["#008f88", "#00b77c", "#b0d64b", "#ffc540", "#ff902a", "#ff0000"];

// ====================================================================================================
// Sentiment colors

// Taken from:
// https://gist.github.com/gskema/2f56dc2e087894ffc756c11e6de1b5ed
/**
 * You may use this function with both 2 or 3 interval colors for your gradient.
 * For example, you want to have a gradient between Bootstrap's danger-warning-success colors.
 */
function colorGradient(fadeFraction, rgbColor1, rgbColor2, rgbColor3) {
  var color1 = rgbColor1;
  var color2 = rgbColor2;
  var fade = fadeFraction;

  // Do we have 3 colors for the gradient? Need to adjust the params.
  if (rgbColor3) {
    fade = fade * 2;

    // Find which interval to use and adjust the fade percentage
    if (fade >= 1) {
      fade -= 1;
      color1 = rgbColor2;
      color2 = rgbColor3;
    }
  }

  var diffRed = color2.red - color1.red;
  var diffGreen = color2.green - color1.green;
  var diffBlue = color2.blue - color1.blue;

  var gradient = {
    red: parseInt(Math.floor(color1.red + diffRed * fade), 10),
    green: parseInt(Math.floor(color1.green + diffGreen * fade), 10),
    blue: parseInt(Math.floor(color1.blue + diffBlue * fade), 10),
  };

  return (
    "rgb(" + gradient.red + "," + gradient.green + "," + gradient.blue + ")"
  );
}

window.onload = function () {
  // Get all the elements with class="sentiment-text"
  let texts = document.getElementsByClassName("sentiment-text");

  // Loop through all the texts
  for (let i = 0; i < texts.length; i++) {
    let text = texts[i];
    let sentiment = parseFloat(text.innerHTML);
    let percentage = (sentiment + 1) / 2;
    var color = colorGradient(
      percentage,
      { red: 255, green: 0, blue: 0 },
      { red: 255, green: 255, blue: 0 },
      { red: 0, green: 255, blue: 0 }
    );

    text.style.color = color;
  }
};
