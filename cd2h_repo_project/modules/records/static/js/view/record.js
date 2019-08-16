const ClipboardJS = require("node_modules/clipboard/dist/clipboard")

const clip = new ClipboardJS('.clipboard-btn');
const $tooltip = $('[data-toggle="tooltip"]');
$tooltip.tooltip();  // Initializes tooltips
$tooltip.on('show.bs.tooltip', () => {
  $('.tooltip').not(this).remove();
});
