import {Component, OnInit} from '@angular/core';
import {UserService} from "../services/user.service";
import {FilesService} from "../services/files.service";
import {FileBasicInfo} from "../model/FileBasicInfo";
import {FileTypeEnum} from "../model/enums/FileTypeEnum";
import {FormControl, FormGroup, Validators} from "@angular/forms";
import {Tag} from "../model/Tag";
import {NotificationsService} from "../services/notifications.service";
import {PresignedUrlRequest} from "../model/PresignedUrlRequest";

@Component({
  selector: 'app-main-page',
  templateUrl: './main-page.component.html',
  styleUrls: ['./main-page.component.css']
})
export class MainPageComponent implements OnInit{

  files! : FileBasicInfo[];
  tags : Tag[] = [];
  uploadedFile!: File;
  enableUpload = false;
  thumbnails : string[] = [];
  constructor(private userService : UserService,
              private notificationService: NotificationsService,
              private fileService: FilesService) {}

  tagForm = new FormGroup({
    tagName: new FormControl('',[Validators.required]),
    tagValue: new FormControl( '',[Validators.required]),
  })

  public ngOnInit() {
    const token = window.location.href.split("#")[1].split("=")[1].split("&")[0];
    this.userService.login(token);
    this.fileService.getUserFiles().subscribe( result => {
      let objects = JSON.parse(result.toString())
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

  public onFileSelected(event : any) : void {
    const files = event.target.files;
    if(files.length == 0) this.enableUpload = false;
    else this.enableUpload = true;
    this.uploadedFile = files[0];
  }

  public addTag() : void {
    if(this.tagForm.valid) {
        const tag : Tag = {
          name : <string>this.tagForm.controls['tagName'].value,
          value : <string>this.tagForm.controls['tagValue'].value
        }
        if(this.checkIfTagIsAdded(tag.name)) {
          this.notificationService.createNotification("Tag with that name already created!")
          return;
        }
        this.tags.push(tag);
    }
  }

  public removeTag(tag : Tag) : void {
    let index = -1;
    for(const t of this.tags) {
      if (t.name == tag.name) {
        index = this.tags.indexOf(t);
        break;
      }
    }
    if (index >= 0) {
      this.tags.splice(index, 1);
    }
  }

  checkIfTagIsAdded(name : string) : boolean {
    for(const tag of this.tags) {
      if(tag.name == name) return true;
    }
    return false;
  }

  public upload() : void {
    const fileInfo : PresignedUrlRequest = {
      type : this.uploadedFile.type,
      size: this.uploadedFile.size,
      name : this.uploadedFile.name
    }
    this.fileService.requestUpload(fileInfo).subscribe( {
      next : response => {
          if(response.hasOwnProperty('errorMessage')) {
            this.notificationService.createNotification(response.errorMessage);
            return;
          }
          const uploadInfo = JSON.parse(JSON.stringify(response));
          const formData = this.generateFormData(uploadInfo);
          this.fileService.uploadFile(uploadInfo["url"],formData).subscribe({
            next: () => {
                  const now = new Date();
                  const metadata = new Map();
                  metadata.set("file_name",this.uploadedFile.name);
                  metadata.set("type",this.uploadedFile.type);
                  metadata.set("size",this.uploadedFile.size);
                  metadata.set("creation_date",now);
                  metadata.set("last_modification_date",now);
                  console.log(this.tags);
                  this.tags.forEach((tag) => {
                    metadata.set(tag.name,tag.value);
                  });
                  this.fileService.uploadMetaData(Object.fromEntries(metadata.entries())).subscribe( {
                    next: (response) => {
                        this.notificationService.createNotification(response);
                    },
                    error: (error) => {
                      console.log(error);
                    }
                  })
            },
            error: err => {
              console.log(err);
            }
          })
      },
      error : error => {
        console.log(error)
      }
    })
  }

  private generateFormData(uploadInfo: any) : FormData {
    const formData = new FormData();
    formData.append("key",uploadInfo["fields"]["key"]);
    formData.append("x-amz-algorithm",uploadInfo["fields"]["x-amz-algorithm"]);
    formData.append("x-amz-credential",uploadInfo["fields"]["x-amz-credential"]);
    formData.append("x-amz-date",uploadInfo["fields"]["x-amz-date"]);
    formData.append("x-amz-security-token",uploadInfo["fields"]["x-amz-security-token"]);
    formData.append("policy",uploadInfo["fields"]["policy"]);
    formData.append("x-amz-signature",uploadInfo["fields"]["x-amz-signature"]);
    formData.append("file",this.uploadedFile,this.uploadedFile.name);
    return formData;
  }
}
