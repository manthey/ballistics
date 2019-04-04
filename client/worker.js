import * as utils from './utils.js';

onmessage = function () {  /* This could take an event */
  fetch('totallist.json').then(resp => resp.json()).catch(err => {
    console.log(err);
    throw err;
  }).then(data => {
    try {
      let pointkeys = utils.updatePointKeys(data);
      let result = {plotdata: data, pointkeys: pointkeys};
      postMessage(result);
    } catch (err) {
      console.error('Worker error', err);
    }
    return null;
  }).catch(err => {
    console.log(err);
    throw err;
  });

  fetch('trajectories.json').then(resp => resp.json()).catch(err => {
    console.log(err);
    throw err;
  }).then(data => {
    try {
      let keys = ['Re', 'Mn', 'time'];
      let trajectories = {};
      data.forEach(entry => {
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
}
