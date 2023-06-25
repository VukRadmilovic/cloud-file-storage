import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {FileBasicInfo} from "../model/FileBasicInfo";
import {Observable} from "rxjs";
import {baseURL} from "../environments/baseURLs";
import {UserService} from "./user.service";
import {PresignedUrlRequest} from "../model/PresignedUrlRequest";

@Injectable({
  providedIn: 'root'
})

export class FilesService {
  constructor(private http: HttpClient,
              private userService: UserService) {}

  private headers = new HttpHeaders({
    skip: 'true',
  });

  public getUserFiles() : Observable<FileBasicInfo[]> {
    return this.http.get<FileBasicInfo[]>(baseURL + 'get-user-data?username=' + this.userService.getLoggedUsername() + "&album=0");
  }

  public requestUpload(metadata : any) : Observable<any> {
    return this.http.post<any>(baseURL + "upload-link?username=" + this.userService.getLoggedUsername(), metadata);
  }

  public uploadFile(url: string, fileInfo: FormData) : Observable<any> {
    return this.http.post(url, fileInfo, {headers:this.headers});
  }

  public getFileData(filePath : string) : Observable<any> {
    return  this.http.get<any>(baseURL + "/get-file-details?username=" + this.userService.getLoggedUsername() + "&file_path=" + filePath);
  }

}
