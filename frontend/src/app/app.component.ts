import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Latest } from './models/Latest';

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
            this.interval = setInterval(() => {
                this.http.get('/api/actuators').subscribe(data => {
                    this.actuators = data;
                });
                this.http.get<Latest>('/api/latest').subscribe(data => {
                    let t = this.data['temperature']["data"]

                    for (let item of this.metrics) {
                            this.data[item]['trend'] = data[item][2];
                        }

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

    private getWeather() {
        this.weatherLoad = true;
        this.http.get('/api/weather').subscribe(data => {
            this.weather = data['weather'];
            this.forecast = data['forecast']
            this.weatherLoad = false;
        })
    }

}
