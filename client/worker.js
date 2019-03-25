import * as utils from './utils.js';

onmessage = function () {  /* This could take an event */
  fetch('totallist.json').then(resp => resp.json()).then(data => {
    try {
      let pointkeys = utils.updatePointKeys(data);
      let result = {plotdata: data, pointkeys: pointkeys};
      postMessage(result);
    } catch (err) {
      console.exception('Worker error', err);
    }
    return null;
  }).catch(err => {
    console.log(err);
    throw err;
  });
}
