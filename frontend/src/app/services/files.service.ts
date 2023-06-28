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

  public getUserFiles(path: string) : Observable<FileBasicInfo[]> {
    return this.http.get<FileBasicInfo[]>(baseURL + 'get-user-data?username=' + this.userService.getLoggedUsername() + "&album=" + path);
  }
  public getUserSharedFiles(path: string) : Observable<FileBasicInfo[]> {
    return this.http.get<FileBasicInfo[]>(baseURL + 'get-user-shared-data?username=' + this.userService.getLoggedUsername() + "&album=" + path);
  }

  public requestUpload(metadata : any) : Observable<any> {
    return this.http.post<any>(baseURL + "upload-link?username=" + this.userService.getLoggedUsername(), metadata);
  }

  public modifyMetadataOnly(metadata: any) : Observable<any> {
    return this.http.put<any>(baseURL + "modify-metadata?username=" + this.userService.getLoggedUsername(),metadata);
  }

  public modifyFile(file: File, url: string) : Observable<any> {
    return this.http.put(url,file, {headers: this.headers});
  }

  public requestFullModification(metadata: any) : Observable<any> {
    return this.http.put<any>(baseURL + "modify-full?username=" + this.userService.getLoggedUsername(), metadata);
  }

  public uploadFile(url: string, fileInfo: FormData) : Observable<any> {
    return this.http.post(url, fileInfo, {headers:this.headers});
  }

  public getFileData(filePath : string) : Observable<any> {
    return  this.http.get<any>(baseURL + "/get-file-details?username=" + this.userService.getLoggedUsername() + "&file_path=" + filePath);
  }

  public deleteFile(file_path: string): Observable<any> {
    return this.http.delete(baseURL + "delete-item?username=" + this.userService.getLoggedUsername() + "&file_path=" + file_path);
  }

  downloadFile(filePath: string): Observable<any> {
    const url = baseURL + "download-file?username=" + this.userService.getLoggedUsername() + "&file_path=" + filePath;
    return this.http.get(url);
  }

  createAlbum(current_path: string) {
    current_path = this.userService.getLoggedUsername() + current_path;
    const url = baseURL + "create-album?username=" + this.userService.getLoggedUsername() + "&file_path=" + current_path;
    return this.http.get(url);
  }

  deleteAlbum(current_path: string) : Observable<string> {
    current_path = this.userService.getLoggedUsername() + current_path;
    const url = baseURL + "delete-album?username=" + this.userService.getLoggedUsername() + "&file_path=" + current_path;
    return this.http.delete<string>(url);
  }

  public family(shareUser: string) : Observable<any>{
    const url = baseURL + "family-album?user=" + this.userService.getLoggedUsername() + "&family=" + shareUser;
    return this.http.post<string>(url, {});
  }

  shareAlbum(current_path: string, shareTo: string) : Observable<string> {
    current_path = this.userService.getLoggedUsername() + current_path;
    const url = baseURL + "share-album?sharedFrom=" + this.userService.getLoggedUsername() + "&file_path=" + current_path + "&sharedTo=" + shareTo;
    return this.http.post<string>(url, {});
  }

  stopShareAlbum(current_path: string, shareTo: string) : Observable<string> {
    current_path = this.userService.getLoggedUsername() + current_path;
    const url = baseURL + "stop-share-album?sharedFrom=" + this.userService.getLoggedUsername() + "&file_path=" + current_path + "&sharedTo=" + shareTo;
    return this.http.delete<string>(url);
  }

  copyFile(fileToCopy: string, pathToCopyTo: string) : Observable<string> {
    const fileName = fileToCopy.split("/").pop();
    pathToCopyTo = this.userService.getLoggedUsername() + pathToCopyTo + fileName;
    const url = baseURL + "copy-file?username=" + this.userService.getLoggedUsername() + "&source_path=" + fileToCopy + "&destination_path=" + pathToCopyTo;
    return this.http.put<string>(url, {});
  }

  moveFile(fileToMove: string, pathToMoveTo: string) : Observable<string> {
    const fileName = fileToMove.split("/").pop();
    pathToMoveTo = this.userService.getLoggedUsername() + pathToMoveTo + fileName
    const url = baseURL + "move-file?username=" + this.userService.getLoggedUsername() + "&source_path=" + fileToMove + "&destination_path=" + pathToMoveTo;
    return this.http.put<string>(url, {});
  }
}
