# Cards

Hey cards store a person's contact details and can be viewed, downloaded, and shared as QR codes.

## Card List

Authenticated users land on the card list at `/`. The list only shows cards owned by the current user.

## Card Detail

Each card detail page at `/cards/<id>/` shows the display name, role line, contact fields, QR preview, vCard data, and card actions. The actions include `.vcf` download, fullscreen QR presentation, and QR PNG download.

## QR Codes

### QR PNG

The QR PNG endpoint at `/cards/<id>/qr.png` encodes the card's vCard data and is only available to the card owner. The detail page uses this endpoint for its QR preview and PNG download, and the fullscreen QR page uses the same PNG as its scannable image.

### Fullscreen QR Presentation

The fullscreen QR page at `/cards/<id>/qr/fullscreen/` shows the card name, optional role line, and a large QR code in a mobile-first presentation layout. It is linked from the card detail page and is intended for presenting a card from a phone, tablet, or display while keeping the normal detail page available for editing and downloads.

The fullscreen page includes secondary Back and Download actions. Back returns to `/cards/<id>/`, and Download points to `/cards/<id>/qr.png` so the owner can save the same QR image used for scanning.

## vCard Downloads

The vCard endpoint at `/cards/<id>/vcard.vcf` returns a downloadable `.vcf` file generated from the same card fields used by the QR code.

## Access Control

All card pages and download endpoints are scoped to the logged-in owner. Users cannot view, edit, delete, download, or present another user's card.

Unauthenticated users who request the fullscreen QR page are redirected to login and then back to the requested card page after authentication. The QR PNG and vCard download endpoints return not found unless the request comes from the logged-in owner.
