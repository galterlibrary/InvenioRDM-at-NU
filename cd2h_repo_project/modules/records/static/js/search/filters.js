// Search filters

// startsWith polyfill
if (!String.prototype.startsWith) {
    Object.defineProperty(String.prototype, 'startsWith', {
        value: function(search, pos) {
            pos = !pos || pos < 0 ? 0 : +pos;
            return this.substring(pos, pos + search.length) === search;
        }
    });
}

function ununderscore() {
  /* Convert underscores in the string to spaces */
  return function(text) {
    return text ? String(text).replace('_', ' ') : '';
  };
}

function to_human_readable(mapping) {
  return function(slug) {
    return mapping[String(slug)];
  };
}

function to_license_name() {
  /* Convert license slug to human readable license name */
  return to_human_readable({
    "mit-license": "MIT License",
    "cc-by": "Creative Commons Attribution",
    "cc-by-sa": "Creative Commons Attribution Share-Alike",
    "cc-zero": "Creative Commons CCZero",
    "cc-nc": "Creative Commons Non-Commercial (Any)",
    "gpl-3.0": "GNU General Public License version 3.0 (GPLv3)",
    "other-open": "Other (Open)",
    "other-closed": "Other (Not Open)"
  });
}

function to_subjects_name() {
  /* Convert subjects (terms) source slug to human readable name */
  return to_human_readable({
    "MeSH": "Medical",
    "FAST": "Topical"
  });
}

function to_access_name() {
  /* Convert permissions (access rights) source slug to human readable name */
  return function(slug) {
    if (slug.startsWith('all_')) {
      return 'Open Access';
    } else if (slug.startsWith('restricted_')) {
      return 'Restricted Access';
    } else {
      return 'Private Access';
    }
  }
}

function to_label_css() {
  /* Convert record to Bootstrap 3 label css */
  return function(record) {
    var permissions = record.metadata.permissions;
    if (record.metadata.type != 'draft') {
      if (permissions.startsWith('all_')) {
        return 'label-success';
      } else if (permissions.startsWith('restricted_')) {
        return 'label-warning';
      }
    }
    return 'label-danger'
  }
}


angular.module('invenioSearch')
  .filter('ununderscore', ununderscore)
  .filter('to_license_name', to_license_name)
  .filter('to_subjects_name', to_subjects_name)
  .filter('to_access_name', to_access_name)
  .filter('to_label_css', to_label_css);
