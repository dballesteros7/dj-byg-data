
function InputCtrl($http){
    this._http = $http;
}

InputCtrl.$inject = ['$http'];

function getGenre($event){
    $event.preventDefault();
    this._http({
        method: 'POST',
        url: '/genre',
        data: {
            'lyrics': this.lyrics
        }
    }).then( function(httpData) {
        this.genre = httpData.data;
    }.bind( this ));
}
InputCtrl.prototype.getGenre = getGenre;


angular.module('djtinidata', []).controller('InputCtrl',
    InputCtrl);
