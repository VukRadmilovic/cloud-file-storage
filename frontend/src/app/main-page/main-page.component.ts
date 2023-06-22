import {Component, OnInit} from '@angular/core';
import {UserService} from "../services/user.service";

@Component({
  selector: 'app-main-page',
  templateUrl: './main-page.component.html',
  styleUrls: ['./main-page.component.css']
})
export class MainPageComponent implements OnInit{

  constructor(private userService : UserService) {}

  public ngOnInit() {
    const token = window.location.href.split("#")[1].split("=")[1].split("&")[0];
    this.userService.login(token);
  }
}
