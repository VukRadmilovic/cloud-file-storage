import { Component } from '@angular/core';
import {UserService} from "../services/user.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.css']
})
export class NavigationComponent {
  constructor(private userService: UserService, private router: Router) { }
  public logout() : void {
    this.userService.logout();
    this.router.navigate(['']).then();
  }
}
