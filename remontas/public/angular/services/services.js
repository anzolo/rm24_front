var remBackend = angular.module('remBackend', ['ngResource']);

remBackend.factory('searchMasters', ['$resource',
  function ($resource) {
        return $resource('/api/main/searchMasters');
                }]);

remBackend.factory('lkData', ['$resource',
  function ($resource) {
        return $resource('/api/lk', {}, {
            "init": {
                method: 'GET',
                params: {
                    method: "init"
                }
            }
            //            "saveNew": {
            //                method: 'POST',
            //                params: {
            //                    method: "saveNew"
            //                }
            //            },
            //            "saveEdited": {
            //                method: 'POST',
            //                params: {
            //                    method: "saveEdited"
            //                }
            //            }
        });
                }]);

remBackend.factory('masterMainData', ['$resource',
  function ($resource) {
        return $resource('/api/lk/mainDataSave');
                }]);