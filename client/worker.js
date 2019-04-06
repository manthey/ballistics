import * as utils from './utils.js';
import axios from 'axios';

onmessage = function (evt) {  /* This could take an event */
  switch (evt.data.action) {
    case 'getplotdata':
      axios.get('totallist.json').then(resp => {
        try {
          let pointkeys = utils.updatePointKeys(resp.data);
          let result = {plotdata: resp.data, pointkeys: pointkeys};
          postMessage(result);
        } catch (err) {
          console.error('Worker error', err);
        }
        return null;
      }).catch(err => {
        console.log(err);
        throw err;
      });
      break;
    case 'gettrajectories':
      axios.get('trajectories.json').then(resp => {
        try {
          let keys = ['Re', 'Mn', 'time'];
          let trajectories = {};
          resp.data.forEach(entry => {
            let pointkey = entry.key + '-' + entry.idx, traj = {}, skip = false;
            keys.forEach(key => {
              if (entry['trajectory_' + key] === undefined) {
                skip = true;
                return;
              }
              traj[key] = JSON.parse(entry['trajectory_' + key]);
            });
            if (!skip) {
              trajectories[pointkey] = traj;
            }
          });
          let result = {trajectories: trajectories};
          postMessage(result);
        } catch (err) {
          console.error('Worker error', err);
        }
        return null;
      }).catch(err => {
        console.log(err);
        throw err;
      });
    break;
  }
}
