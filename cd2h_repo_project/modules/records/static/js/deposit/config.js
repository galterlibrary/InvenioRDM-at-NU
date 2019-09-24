function configDeposit($provide, decoratorsProvider, $windowProvider) {

  decoratorsProvider.defineAddOn(
    'bootstrapDecorator',
    'termsselect',
    '/static/templates/deposit-form/termsselect.html'
  );

}

configDeposit.$inject = [
  '$provide',
  'schemaFormDecoratorsProvider',
  '$windowProvider'
];

angular.module('invenioRecords')
  .config(configDeposit);
