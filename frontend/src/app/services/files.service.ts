import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {FileBasicInfo} from "../model/FileBasicInfo";
import {Observable} from "rxjs";
import {baseURL} from "../environments/baseURLs";
import {UserService} from "./user.service";

@Injectable({
  providedIn: 'root'
})
export class FilesService {
  constructor(private http: HttpClient,
              private userService: UserService) {}

  public getUserFiles() : Observable<FileBasicInfo[]> {
    return this.http.get<FileBasicInfo[]>(baseURL + '/get-user-data?username=dracooya23');
  }

}
