/* Copyright 2016 David Manthey
 *
 * Licensed under the Apache License, Version 2.0 ( the "License" ); you may
 * not use this file except in compliance with the License.  You may obtain a
 * copy of the License at
 *   http://www.apache.org/licenses/LICENSE-2.0
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

var References, Results;

/* Load the references if they haven't been loaded.  Either way, return a
 * promise object.
 * Exit: promise: a promise that resolves when the references are loaded. */
function load_references() {
  if (!References) {
    References = {};
    References.fetch = $.getJSON('references.json').done(function (results) {
      var data = results.references;
      References.references = {};
      $.each(data, function (idx, item) {
        References.references[item.key] = item;
      });
      References.fetch = $.when();
    });
  }
  return References.fetch;
}

/* Load a section based on an event or as specified by name.
 * Enter: evt: the event that triggered this.  null or undefined to use the
 *             section name.
 *        section: the section to load, if no event. */
function load_section(evt, section) {
  if (evt) {
    section = $(evt.target).closest('[data-section]').attr('data-section');
  }
  if (!templates[section]) {
    return;
  }
  $('#b-content').empty().append(templates[section]());
  $('.navbar .current').removeClass('current');
  $('.navbar [data-section="' + section + '"]').closest('li').addClass(
    'current');
}

$(function () {
  $('#b-header').append(templates.menu());
  load_section(undefined, $('.navbar .current>a').attr('data-section'));
  $('.navbar [data-section]').on('click', load_section);

  load_references();
});
