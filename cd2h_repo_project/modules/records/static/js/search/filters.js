// Search filters

function ununderscore() {
  /* Convert underscores in the string to spaces */
  return function(text) {
    return text ? String(text).replace('_', ' ') : '';
  };
}

angular.module('invenioSearch')
  .filter('ununderscore', ununderscore);
