import {
  HttpEvent,
  HttpHandler,
  HttpHandlerFn,
  HttpInterceptor,
  HttpRequest,
  HttpResponse,
} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';

export function authInterceptor(
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
) {
  // Clone the request to add the authentication header.
  // console.log('outgoing request', request);
  request = request.clone({ withCredentials: true });
  // console.log('new outgoing request', request);
  // return next(request).pipe(
  //   tap((ev: HttpEvent<any>) => {
  //     console.log('got an event', ev);
  //     if (ev instanceof HttpResponse) {
  //       console.log('event of type response', ev);
  //     }
  //   })
  // );
  return next(request);
}
