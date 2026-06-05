# Cards

Hey cards store a person's contact details and can be viewed, downloaded, and shared as QR codes.

## Card List

Authenticated users land on the card list at `/`. The list only shows cards owned by the current user.

## Card Detail

Each card detail page at `/cards/<id>/` shows the display name, role line, contact fields, QR preview, vCard data, and card actions.

## QR Codes

The QR PNG endpoint at `/cards/<id>/qr.png` encodes the card's vCard data and is only available to the card owner. The detail page uses this endpoint for its QR preview and PNG download.

The fullscreen QR page at `/cards/<id>/qr/fullscreen/` shows the card name and a large QR code in a focused layout. It is intended for presenting a card from a phone, tablet, or display while keeping the normal detail page available for editing and downloads.

## vCard Downloads

The vCard endpoint at `/cards/<id>/vcard.vcf` returns a downloadable `.vcf` file generated from the same card fields used by the QR code.

## Access Control

All card pages and download endpoints are scoped to the logged-in owner. Users cannot view, edit, delete, download, or present another user's card.
