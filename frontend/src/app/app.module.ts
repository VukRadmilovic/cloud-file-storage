import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import {RouterOutlet} from "@angular/router";
import {AppRoutingModule} from "./app-routing.module";
import {InterceptorService} from "./interceptor/interceptor.service";
import {HTTP_INTERCEPTORS, HttpClientModule} from "@angular/common/http";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatTabsModule} from "@angular/material/tabs";
import {MatInputModule} from "@angular/material/input";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {MatButtonModule} from "@angular/material/button";
import {MatSnackBarModule} from "@angular/material/snack-bar";
import {MatTableModule} from "@angular/material/table";
import {MatPaginatorModule} from "@angular/material/paginator";
import {MatDialogModule} from "@angular/material/dialog";
import {MatSortModule} from "@angular/material/sort";
import {MatRadioModule} from "@angular/material/radio";
import {MatSelectModule} from "@angular/material/select";
import {MatDatepickerModule} from "@angular/material/datepicker";
import {MatNativeDateModule} from "@angular/material/core";
import {NgxFileDropModule} from "ngx-file-drop";
import {MatCheckboxModule} from "@angular/material/checkbox";
import { NgxCaptchaModule } from 'ngx-captcha';
import {MatCardModule} from "@angular/material/card";
import { MainPageComponent } from './main-page/main-page.component';
import { LoginComponent } from './login/login.component';
import {JwtModule} from "@auth0/angular-jwt";
import { NavigationComponent } from './navigation/navigation.component';
import {MatGridListModule} from "@angular/material/grid-list";
import {MatChipsModule} from "@angular/material/chips";
import {MatIconModule} from "@angular/material/icon";
import {SharedComponent} from "./shared/shared-component";

@NgModule({
  declarations: [
    AppComponent,
    MainPageComponent,
    LoginComponent,
    NavigationComponent,
    SharedComponent,
  ],
  imports: [
    BrowserModule,
    RouterOutlet,
    JwtModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatTabsModule,
    MatInputModule,
    ReactiveFormsModule,
    HttpClientModule,
    MatButtonModule,
    MatSnackBarModule,
    MatTableModule,
    MatPaginatorModule,
    MatDialogModule,
    MatSortModule,
    MatRadioModule,
    FormsModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    NgxFileDropModule,
    MatCheckboxModule,
    NgxCaptchaModule,
    MatCardModule,
    MatGridListModule,
    MatChipsModule,
    MatIconModule
  ],
  providers: [    {
    provide: HTTP_INTERCEPTORS,
    useClass: InterceptorService,
    multi: true,
  },],
  bootstrap: [AppComponent]
})
export class AppModule { }
