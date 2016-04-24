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

module.exports = function (grunt) {
    var path = require('path');

    var port = Number(grunt.option('port') || '8082');

    /* Returns a json string containing information from the current git
     * repository. */
    var versionInfoObject = function () {
        var gitVersion = grunt.config.get('gitinfo');
        var local = gitVersion.local || {};
        var branch = local.branch || {};
        var current = branch.current || {};
        return JSON.stringify(
            {
                git: !!current.SHA,
                SHA: current.SHA,
                shortSHA: current.shortSHA,
                date: grunt.template.date(new Date(), 'isoDateTime', true),
                apiVersion: grunt.config.get('pkg').version,
                describe: gitVersionObject
            },
            null,
            '  '
        );
    };

    // Project configuration.
    grunt.config.init({
        pkg: grunt.file.readJSON('package.json'),

        jade: {
            options: {
                client: true,
                compileDebug: false,
                namespace: 'templates',
                processName: function (filename) {
                    return path.basename(filename, '.jade');
                }
            },
            core: {
                files: {
                    'built/templates.js': [
                        'client/templates/**/*.jade'
                    ]
                }
            }
        },

        clean: {
            all: ['built']
        },

        copy: {
            results: {
                expand: true,
                cwd: 'results',
                src: ['**/*.json'],
                dest: 'built/results'
            },
            static: {
                expand: true,
                cwd: 'client/static',
                src: ['**/*'],
                dest: 'built'
            }
        },

        express: {
            server: {
                options: {
                    port: port,
                    Xserver: 'testing/test-runners/server.js',
                    bases: ['built']
                }
            }
        },

        folder_list: {
            results: {
                options: { files: true, folders: false },
                cwd: 'built/',
                src: ['results/**/*.json'],
                dest: 'built/resultslist.json'
            }
        },

        stylus: {
            core: {
                files: {
                    'built/app.min.css': [
                        'client/stylesheets/**/*.styl',
                    ]
                }
            }
        },

        shell: {
            getgitversion: {
                command: 'git describe --always --long --dirty --all',
                options: {
                    callback: function (err, stdout, stderr, callback) {
                        gitVersionObject = stdout.replace(/^\s+|\s+$/g, '');
                        callback();
                    }
                }
            }
        },

        yaml: {
            core: {
                files: {
                    'built/references.json': [
                        'data/references.yml',
                    ]
                }
            }
        },

        concat: {
            options: {
                separator: ';',
                sourceMap: true
            },
            app: {
                src: [
                    /* main.js must be first */
                    'client/js/main.js',
                    'built/templates.js',
                    'built/ballistics-version.js',
                    'client/js/**/*.js'
                ],
                dest: 'built/app.js'
            }
        },

        uglify: {
            options: {
                sourceMap: true,
                sourceMapIncludeSources: true,
                report: 'min',
                beautify: {
                    ascii_only: true
                }
            },
            app: {
                options: {
                    sourceMapIn: 'built/app.js.map'
                },
                files: {
                    'built/app.min.js': [
                        'built/app.js'
                    ]
                }
            },
            libs: {
                files: {
                    'built/libs.min.js': [
                        'node_modules/jquery/dist/jquery.js',
                        //'node_modules/d3/d3.js',
                        //'node_modules/mathjax/MathJax.js',
                        //'node_modules/mathjax/config/TeX-AMS_HTML.js',
                        'node_modules/plotly.js/dist/plotly.js',
                        'client/lib/**/*.js'
                    ]
                }
            }
        },

        'file-creator': {
            app: {
                'built/ballistics-version.js': function (fs, fd, done) {
                    var ballisticsVersion = versionInfoObject();
                    fs.writeSync(
                        fd,
                        [
                            'ballisticsVersionInfo = ' +
                            ballisticsVersion +
                            ';\n'
                        ].join('\n')
                    );
                    done();
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jade');
    grunt.loadNpmTasks('grunt-contrib-stylus');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-express');
    grunt.loadNpmTasks('grunt-file-creator');
    grunt.loadNpmTasks('grunt-folder-list');
    grunt.loadNpmTasks('grunt-gitinfo');
    grunt.loadNpmTasks('grunt-shell');
    grunt.loadNpmTasks('grunt-yaml');

    var defaultTasks = [
        'stylus',
        'build-js',
        'yaml',
        'copy:static',
        'copy:results',
        'folder_list:results'
    ];

    grunt.registerTask('version-info', [
        'gitinfo',
        'shell:getgitversion',
        'file-creator:app'
    ]);
    grunt.registerTask('build-js', [
        'jade',
        'version-info',
        'concat:app',
        'uglify:app'
    ]);
    grunt.registerTask('init', [
        'uglify:libs'
    ]);
    grunt.registerTask('serve',
        'Serve the content at http://localhost:8082, ' +
        'use the --port option to override the default port', [
        'express',
        'express-keepalive'
    ]);
    grunt.registerTask('default', defaultTasks);
};
