import {FileTypeEnum} from "./enums/FileTypeEnum";

export interface FileBasicInfo {
  file: string,
  type: FileTypeEnum,
  date_created : Date,
  url: string
}
