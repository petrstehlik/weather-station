import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Latest } from './models/Latest';
import { environment as env } from 'environments/environment';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styles: [],
  providers : [HttpClient]
})
export class AppComponent implements OnInit {
    tempData : Object = {'data' : [], 'labels' : []};
    tempLoad = true;
    weatherLoad = true;
    interval = undefined;
    weather = undefined;
    forecast = undefined;
    env = env;

    metrics = ['temperature', 'humidity', 'pressure', 'light', 'moisture'];
    categories = [
        {
            'unit' : '°C',
            'title' : 'Temperature',
            'metric' : 'temperature'
        },
        {
            'unit' : '%',
            'title' : 'Humidity',
            'metric' : 'humidity'
        },
        {
            'unit' : 'hPa',
            'title' : 'Pressure',
            'metric' : 'pressure'
        },
        {
            'unit' : '%',
            'title' : 'Light',
            'metric' : 'light'
        },
        {
            'unit' : '%',
            'title' : 'Moisture',
            'metric' : 'moisture'
        }]

    actuators;
    data : Object = {
        temperature : undefined,
        humidity : undefined,
        pressure : undefined,
        light : undefined,
        moisture : undefined
    };

    constructor(private http: HttpClient, private ref: ChangeDetectorRef) {}

    ngOnInit() {
        this.getWeather();
        this.http.get('/api/init').subscribe(data => {
            this.data = data;
            this.parseData();
            this.getTrends();
            this.getActuators();
            this.interval = setInterval(() => {
                this.http.get<Latest>('/api/latest').subscribe(data => {
                     this.getTrends(data);
                     let t = this.data['temperature']["data"]

                    // Don't do anything if we have still old data
                    if (t[t.length - 1][0].getTime() == new Date(data['temperature'][0]).getTime()) {
                        return;
                    }

                    this.tempLoad = true;

                    for (let item of this.metrics) {
                        let newdata = this.data;
                        this.data[item]['data'].push([new Date(data[item][0]), data[item][1]]);
                        this.ref.markForCheck();
                        this.ref.detectChanges();
                    }

                    this.tempLoad = false;
                })
            }, 5000);
        });
    }

    toggleActuator(act) {
        console.log("should change", act);
    }

    updateActuator(act) {
        console.log(act);
        this.http.post('/api/actuators/' + act.id, act.thresholds).subscribe(data => {
            console.log(data)
            act = data;
            act.active = true;

            for(let item of this.actuators) {
                if (item.id == act.id) {
                    item = act;
                }
            }
        })
    }

    private parseData() {
        for (let metric of this.metrics) {
            for (let item of this.data[metric] ) {
                item[0] = new Date(item[0])
            }

            this.data[metric] = {
                "labels" : [metric, 'Value'],
                "data" : this.data[metric],
                "trend" : 0
            }
        }

        this.tempLoad = false;
    }

    private getActuators() {
        this.http.get('/api/actuators').subscribe(data => {
            this.actuators = data;
        });
    }

    private getTrends(data = undefined) {
        if (data === undefined) {
            this.http.get<Latest>('/api/latest').subscribe(data => {
                for (let item of this.metrics) {
                    this.data[item]['trend'] = data[item][2];
                }
            });
        } else {
            for (let item of this.metrics) {
                this.data[item]['trend'] = data[item][2];
            }
        }
    }

    private getWeather() {
        this.weatherLoad = true;
        this.http.get('/api/weather').subscribe(data => {
            this.weather = data['weather'];
            this.forecast = data['forecast']
            this.weatherLoad = false;
        })
    }

}
