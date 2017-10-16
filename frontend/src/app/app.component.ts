import { Component, OnInit } from '@angular/core';

declare const Dygraph;
declare const socketio;

@Component({
  selector: 'app-root',
  template: `
    <h1>
      Welcome to {{title}}!!
    </h1>

    <div id="chart"></div>
  `,
  styles: []
})
export class AppComponent implements OnInit {
    title = 'app';

    g = null;

    ngOnInit() {
        console.log("hello");
        this.g = new Dygraph("chart", [[1,2], [2,1]])
    }
}
