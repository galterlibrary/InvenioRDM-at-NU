// Search filters

function ununderscore() {
  /* Convert underscores in the string to spaces */
  return function(text) {
    return text ? String(text).replace('_', ' ') : '';
  };
}

function to_license_name() {
  /* Convert license slug to human readable license name */
  return function(slug) {
    var slug_to_license = {
      "mit-license": "MIT License",
      "cc-by": "Creative Commons Attribution",
      "cc-by-sa": "Creative Commons Attribution Share-Alike",
      "cc-zero": "Creative Commons CCZero",
      "cc-nc": "Creative Commons Non-Commercial (Any)",
      "gpl-3.0": "GNU General Public License version 3.0 (GPLv3)",
      "other-open": "Other (Open)",
      "other-closed": "Other (Not Open)"
    };
    return slug_to_license[String(slug)];
  };
}

function to_subjects_name() {
  /* Convert subjects (terms) source slug to human readable name */
  return function(slug) {
    var slug_to_name = {
      "MeSH": "Medical",
      "FAST": "Topical"
    };
    return slug_to_name[String(slug)];
  };
}

angular.module('invenioSearch')
  .filter('ununderscore', ununderscore)
  .filter('to_license_name', to_license_name)
  .filter('to_subjects_name', to_subjects_name);
