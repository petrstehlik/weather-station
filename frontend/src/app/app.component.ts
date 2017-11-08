import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  template: `
    <h1>
      Weather Station
    </h1>

    <small class="ts">
        {{ data['temperature']['data'][data['temperature']['data'].length-1][0] | date : 'HH:mm:ss dd/M' }}
    </small>

<div class="cards">
    <div class="card" *ngFor="let c of categories" [ngClass]="c['metric']">
        <h3>{{ c['title'] }}</h3>
        <div class="big-num" *ngIf="!tempLoad">
            {{ data[c['metric']]['data'][data[c['metric']]['data'].length-1][1] | number : '1.1-2' }} {{ c['unit'] }}
        </div>

        <div class="graph">
            <ex-graph
                height="75"
                [(data)]="data[c['metric']]"
                labels="null"
                [loading]="tempLoad"
                range="null"
                topTitle="null"
                labelY="null"
            ></ex-graph>
        </div>
    </div>

    <div class="card">
        <h3>Temp Outside</h3>
        <div class="big-num" *ngIf="!weatherLoad">
            Some val °C
        </div>

        <div class="weather-item" *ngFor="let item of weather['list'] | slice:0:5">
        Time: {{ item['dt'] }}
        Temp : {{ item['main']['temp'] }}
            {{ item | json }}
        </div>
    </div>

</div>


  `,
  styles: [],
  providers : [HttpClient]
})
export class AppComponent implements OnInit {
    tempData : Object = {'data' : [], 'labels' : []};
    tempLoad = true;
    weatherLoad = false;
    interval = undefined;
    weather = undefined;

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
            'unit' : 'Pa',
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

    ws;
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
                this.http.get('/api/latest').subscribe(data => {
                    let t = this.data['temperature']["data"]

                    // Don't do anything if we have still old data
                    if (t[t.length - 1][0].getTime() == new Date(data['temperature'][0]).getTime())
                        return

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
                "data" : this.data[metric]
            }
        }

        this.tempLoad = false;
    }

    private getWeather() {
        this.http.get('/api/weather').subscribe(data => {
            this.weather = data;
        })
    }

}
