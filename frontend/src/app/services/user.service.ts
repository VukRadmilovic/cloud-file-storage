import { Injectable } from '@angular/core';
import {timer} from "rxjs";
import {NotificationsService} from "./notifications.service";
import {Router} from "@angular/router";
import {JwtHelperService} from "@auth0/angular-jwt";
@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private router : Router,
              private notificationService: NotificationsService) { }

  public login(token: string) {
    sessionStorage.setItem('user',token);
    timer(3600000).subscribe(x => this.forceLogout());
  }

  public logout(): void {
    sessionStorage.removeItem('user');
  }

  public forceLogout() : void {
    if(sessionStorage.getItem('user') == null) return;
    this.notificationService.createNotification("Session expired. You will be redirected to the login page.");
    timer(5000).subscribe(x => {
      if(sessionStorage.getItem('user') == null) return;
      this.logout();
      this.router.navigate([''])});
  }

  public getLoggedUsername() : string {
    const helper = new JwtHelperService();
    const token: string | null = sessionStorage.getItem('user')
    if(token != null) {
      return helper.decodeToken(token)["cognito:username"];
    }
    return "";
  }

}
