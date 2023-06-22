import { Component } from '@angular/core';
import {loginURL} from "../environments/baseURLs";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  constructor() { window.location.href = loginURL; }
}
