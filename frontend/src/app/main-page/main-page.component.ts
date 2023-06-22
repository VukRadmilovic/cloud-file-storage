import {Component, OnInit} from '@angular/core';
import {UserService} from "../services/user.service";
import {FilesService} from "../services/files.service";
import {FileBasicInfo} from "../model/FileBasicInfo";
import {FileTypeEnum} from "../model/enums/FileTypeEnum";

@Component({
  selector: 'app-main-page',
  templateUrl: './main-page.component.html',
  styleUrls: ['./main-page.component.css']
})
export class MainPageComponent implements OnInit{

  files! : FileBasicInfo[];
  thumbnails : string[] = [];
  constructor(private userService : UserService,
              private fileService: FilesService) {}

  public ngOnInit() {
    const token = window.location.href.split("#")[1].split("=")[1].split("&")[0];
    this.userService.login(token);
    this.fileService.getUserFiles().subscribe( result => {
      let objects = JSON.parse(result.toString())
      if(objects.length == 0) return;
      this.files = objects;
      this.files.forEach((file) => {
        const tokens = file.file.split("/");
        file.file = tokens[tokens.length - 1];
        if(file.type == FileTypeEnum.APPLICATION || file.type == FileTypeEnum.TEXT) this.thumbnails.push("assets/images/text.png");
        else if(file.type == FileTypeEnum.AUDIO) this.thumbnails.push("assets/images/audio.png");
        else if(file.type == FileTypeEnum.VIDEO) this.thumbnails.push("assets/images/video.png");
        else if(file.type == FileTypeEnum.FOLDER) {
          file.file = tokens[tokens.length - 2];
          this.thumbnails.push("assets/images/folder.png");
        }
        else this.thumbnails.push(file.url);
      })
    });
  }
}
